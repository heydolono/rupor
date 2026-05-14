import logging
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class ModerationService:
    _text_classifier = None
    _image_classifier = None

    TOXICITY_THRESHOLD = 0.7
    NSFW_THRESHOLD = 0.7

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
            result = classifier(text[:512])[0]
            label = result['label']
            score = result['score']
            is_toxic = label == 'toxic' and score >= cls.TOXICITY_THRESHOLD
            return {
                'is_toxic': is_toxic,
                'toxicity_score': round(score, 4),
                'label': label,
            }
        except Exception as e:
            logger.error(f'Text moderation error: {e}')
            return {'is_toxic': False, 'toxicity_score': 0.0, 'label': 'non-toxic', 'error': str(e)}

    @classmethod
    def check_image(cls, image_file):
        if image_file is None:
            return {'is_nsfw': False, 'nsfw_score': 0.0}

        classifier = cls._get_image_classifier()
        if classifier is None:
            return {'is_nsfw': False, 'nsfw_score': 0.0, 'error': 'model_not_loaded'}

        try:
            image = Image.open(BytesIO(image_file.read()))
            image_file.seek(0)
            result = classifier(image)[0]
            label = result['label']
            score = result['score']
            is_nsfw = label == 'nsfw' and score >= cls.NSFW_THRESHOLD
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
        if text_result.get('is_toxic'):
            reasons.append(
                f'Токсичный текст (скор: {text_result["toxicity_score"]})'
            )

        image_result = cls.check_image(image_file)
        if image_result.get('is_nsfw'):
            reasons.append(
                f'NSFW-изображение (скор: {image_result["nsfw_score"]})'
            )

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
        if not tag_embeddings:
            return []

        content_embedding = model.encode(content, show_progress_bar=False)

        similarities = []
        for i, tag_emb in enumerate(tag_embeddings):
            sim = float(content_embedding @ tag_emb.T) / (
                float((content_embedding ** 2).sum()) ** 0.5 *
                float((tag_emb ** 2).sum()) ** 0.5 + 1e-8
            )
            if sim >= cls.SIMILARITY_THRESHOLD:
                similarities.append({
                    **cls._tags_cache[i],
                    'score': round(sim, 4),
                })

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
        embedding = model.encode(content, show_progress_bar=False)
        return embedding.tolist()

    @classmethod
    def find_similar(cls, blog, request=None, max_results=None):
        if max_results is None:
            max_results = cls.MAX_RESULTS

        if blog.embedding is None:
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
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
