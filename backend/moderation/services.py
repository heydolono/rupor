import logging
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class ModerationService:
    _text_classifier = None
    _image_classifier = None

    TOXICITY_THRESHOLD = 0.7
    NSFW_THRESHOLD = 0.7

    TOXIC_LABELS = {'toxic', 'label_1', '1'}
    SAFE_LABELS = {'non-toxic', 'non_toxic', 'neutral', 'normal', 'label_0', '0'}
    NSFW_LABELS = {'nsfw', 'porn', 'sexy', 'hentai', 'drawings'}
    TEXT_CHUNK_SIZE = 512

    @classmethod
    def _iter_text_chunks(cls, text):
        text = text.strip()
        for start in range(0, len(text), cls.TEXT_CHUNK_SIZE):
            chunk = text[start:start + cls.TEXT_CHUNK_SIZE].strip()
            if chunk:
                yield chunk

    @classmethod
    def _get_text_classifier(cls):
        if cls._text_classifier is None:
            try:
                from transformers import pipeline
                cls._text_classifier = pipeline(
                    'text-classification',
                    model='SkolkovoInstitute/russian_toxicity_classifier',
                )
                logger.info('Text moderation model loaded')
            except Exception as e:
                logger.warning(f'Failed to load text model: {e}')
                cls._text_classifier = False
        return cls._text_classifier if cls._text_classifier is not False else None

    @classmethod
    def _get_image_classifier(cls):
        if cls._image_classifier is None:
            try:
                from transformers import pipeline
                cls._image_classifier = pipeline(
                    'image-classification',
                    model='Falconsai/nsfw_image_detection',
                )
                logger.info('Image moderation model loaded')
            except Exception as e:
                logger.warning(f'Failed to load image model: {e}')
                cls._image_classifier = False
        return cls._image_classifier if cls._image_classifier is not False else None

    @classmethod
    def check_text(cls, text):
        if not text or not text.strip():
            return {'is_toxic': False, 'toxicity_score': 0.0, 'label': 'non-toxic'}

        classifier = cls._get_text_classifier()
        if classifier is None:
            return {'is_toxic': False, 'toxicity_score': 0.0, 'label': 'non-toxic', 'error': 'model_not_loaded'}

        try:
            best_result = {'is_toxic': False, 'toxicity_score': 0.0, 'label': 'non-toxic'}
            for chunk in cls._iter_text_chunks(text):
                result = classifier(chunk)[0]
                label = str(result.get('label', '')).lower()
                score = float(result.get('score', 0.0))
                is_toxic = (
                    label in cls.TOXIC_LABELS
                    and score >= cls.TOXICITY_THRESHOLD
                )
                if is_toxic:
                    return {
                        'is_toxic': True,
                        'toxicity_score': round(score, 4),
                        'label': label,
                    }
                if score > best_result['toxicity_score']:
                    best_result = {
                        'is_toxic': False,
                        'toxicity_score': round(score, 4),
                        'label': label,
                    }
            return best_result
        except Exception as e:
            logger.error(f'Text moderation error: {e}')
            return {'is_toxic': False, 'toxicity_score': 0.0, 'label': 'non-toxic', 'error': str(e)}

    @classmethod
    def check_image(cls, image_file):
        if not image_file or not getattr(image_file, 'name', None):
            return {'is_nsfw': False, 'nsfw_score': 0.0}

        classifier = cls._get_image_classifier()
        if classifier is None:
            return {'is_nsfw': False, 'nsfw_score': 0.0, 'error': 'model_not_loaded'}

        try:
            image = Image.open(BytesIO(image_file.read())).convert('RGB')
            image_file.seek(0)
            results = classifier(image)
            nsfw_result = next(
                (
                    item for item in results
                    if str(item.get('label', '')).lower() in cls.NSFW_LABELS
                ),
                results[0] if results else {},
            )
            label = str(nsfw_result.get('label', '')).lower()
            score = float(nsfw_result.get('score', 0.0))
            is_nsfw = label in cls.NSFW_LABELS and score >= cls.NSFW_THRESHOLD
            return {
                'is_nsfw': is_nsfw,
                'nsfw_score': round(score, 4),
                'label': label,
            }
        except Exception as e:
            logger.error(f'Image moderation error: {e}')
            return {'is_nsfw': False, 'nsfw_score': 0.0, 'error': str(e)}

    @classmethod
    def moderate_blog(cls, text, image_file=None):
        reasons = []

        text_result = cls.check_text(text)
        if text_result.get('error'):
            reasons.append(f'Ошибка текстовой модерации: {text_result["error"]}')
        if text_result.get('is_toxic'):
            reasons.append(
                f'Токсичный текст (скор: {text_result["toxicity_score"]})'
            )

        image_result = cls.check_image(image_file)
        if image_result.get('error'):
            reasons.append(f'Ошибка модерации изображения: {image_result["error"]}')
        if image_result.get('is_nsfw'):
            reasons.append(
                f'NSFW-изображение (скор: {image_result["nsfw_score"]})'
            )

        if text_result.get('error') or image_result.get('error'):
            return {
                'moderation_status': 'pending',
                'moderation_reason': '; '.join(reasons),
            }
        if reasons:
            return {
                'moderation_status': 'blocked',
                'moderation_reason': '; '.join(reasons),
            }
        return {
            'moderation_status': 'approved',
            'moderation_reason': None,
        }

    @classmethod
    def moderate_comment(cls, text):
        text_result = cls.check_text(text)
        if text_result.get('error'):
            return {
                'moderation_status': 'pending',
                'moderation_reason': (
                    f'Ошибка текстовой модерации: {text_result["error"]}'
                ),
            }
        if text_result.get('is_toxic'):
            return {
                'moderation_status': 'blocked',
                'moderation_reason': (
                    f'Токсичный комментарий (скор: {text_result["toxicity_score"]})'
                ),
            }
        return {
            'moderation_status': 'approved',
            'moderation_reason': None,
        }


class TagSuggestionService:
    _model = None
    _tag_embeddings = None
    _tags_cache = None

    SIMILARITY_THRESHOLD = 0.3

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(
                    'paraphrase-multilingual-MiniLM-L12-v2'
                )
                logger.info('Tag suggestion model loaded')
            except Exception as e:
                logger.warning(f'Failed to load tag suggestion model: {e}')
                cls._model = False
        return cls._model if cls._model is not False else None

    @classmethod
    def _get_tag_embeddings(cls):
        if cls._tag_embeddings is None:
            from rupor.models import Tag
            tags = list(Tag.objects.all().values('id', 'name', 'slug', 'color'))
            if not tags:
                cls._tags_cache = []
                cls._tag_embeddings = []
                return []
            model = cls._get_model()
            if model is None:
                return []
            tag_names = [t['name'] for t in tags]
            embeddings = model.encode(tag_names, show_progress_bar=False)
            cls._tags_cache = tags
            cls._tag_embeddings = embeddings
        return cls._tag_embeddings

    @classmethod
    def suggest(cls, title, text=None):
        content = title
        if text:
            content += ' ' + text

        if not content.strip():
            return []

        model = cls._get_model()
        if model is None:
            return []

        tag_embeddings = cls._get_tag_embeddings()
        if tag_embeddings is None or len(tag_embeddings) == 0:
            return []

        try:
            content_embedding = model.encode(content, show_progress_bar=False)

            similarities = []
            for i, tag_emb in enumerate(tag_embeddings):
                sim = SemanticSearchService._cosine_similarity(
                    content_embedding,
                    tag_emb,
                )
                if sim >= cls.SIMILARITY_THRESHOLD:
                    similarities.append({
                        **cls._tags_cache[i],
                        'score': round(sim, 4),
                    })
        except Exception as e:
            logger.error(f'Tag suggestion error: {e}')
            return []

        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities

    @classmethod
    def clear_cache(cls):
        cls._model = None
        cls._tag_embeddings = None
        cls._tags_cache = None


class SemanticSearchService:
    _model = None

    SIMILARITY_THRESHOLD = 0.3
    MAX_RESULTS = 5

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(
                    'paraphrase-multilingual-MiniLM-L12-v2'
                )
                logger.info('Semantic search model loaded')
            except Exception as e:
                logger.warning(f'Failed to load semantic search model: {e}')
                cls._model = False
        return cls._model if cls._model is not False else None

    @classmethod
    def compute_embedding(cls, title, text=None):
        content = title
        if text:
            content += ' ' + text
        if not content.strip():
            return None
        model = cls._get_model()
        if model is None:
            return None
        try:
            embedding = model.encode(content, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f'Embedding computation error: {e}')
            return None

    @classmethod
    def find_similar(cls, blog, request=None, max_results=None):
        if max_results is None:
            max_results = cls.MAX_RESULTS

        if not blog.embedding:
            return []

        from rupor.models import Blog as BlogModel
        qs = BlogModel.objects.exclude(id=blog.id).exclude(
            moderation_status='blocked'
        )
        if request and request.user.is_authenticated:
            qs = qs.filter(moderation_status='approved') | qs.filter(
                author=request.user
            )
        else:
            qs = qs.filter(moderation_status='approved')
        qs = qs.distinct()

        blog_emb = blog.embedding
        scored = []
        for other in qs.iterator(chunk_size=100):
            if other.embedding is None:
                continue
            sim = cls._cosine_similarity(blog_emb, other.embedding)
            if sim >= cls.SIMILARITY_THRESHOLD:
                scored.append((other, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:max_results]]

    @staticmethod
    def _cosine_similarity(a, b):
        a = list(a)
        b = list(b)
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
