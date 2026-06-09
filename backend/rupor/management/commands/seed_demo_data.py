from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image, ImageDraw

from rupor.models import Blog, Comment, Favourite, Like, Tag
from users.models import Subscribe, User


PASSWORD = 'RuporDemo2026!'


class Command(BaseCommand):
    help = 'Create deterministic demo data for Rupor.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Write demo data. Without this flag the command only prints a plan.',
        )
        parser.add_argument(
            '--reset-namespace',
            action='store_true',
            help='Delete demo objects from this namespace before creating them.',
        )
        parser.add_argument(
            '--namespace',
            default='demo',
            help='Slug/username/email prefix for demo objects.',
        )

    def handle(self, *args, **options):
        namespace = options['namespace'].strip().lower()
        if not namespace:
            raise CommandError('Namespace must not be empty.')

        self.namespace = namespace
        if not options['apply']:
            self.stdout.write(self.style.WARNING('Dry run only. Add --apply to write data.'))
            self._print_plan()
            return

        with transaction.atomic():
            if options['reset_namespace']:
                self._reset_namespace()
            self._create_demo_data()

        self.stdout.write(self.style.SUCCESS('Demo data is ready.'))
        self.stdout.write(f'Users password: {PASSWORD}')

    def _print_plan(self):
        self.stdout.write('Will create or update:')
        self.stdout.write('- 5 users: admin, authors, reader, moderator')
        self.stdout.write('- 8 tags')
        self.stdout.write('- 18 blogs with images and embeddings')
        self.stdout.write('- approved, blocked and pending moderation states')
        self.stdout.write('- comments, likes, favorites and subscriptions')

    def _reset_namespace(self):
        users = User.objects.filter(username__startswith=f'{self.namespace}_')
        Blog.objects.filter(author__in=users).delete()
        Comment.objects.filter(author__in=users).delete()
        Favourite.objects.filter(user__in=users).delete()
        Like.objects.filter(user__in=users).delete()
        Subscribe.objects.filter(user__in=users).delete()
        Subscribe.objects.filter(author__in=users).delete()
        users.delete()
        Tag.objects.filter(slug__startswith=f'{self.namespace}-').delete()

    def _create_demo_data(self):
        users = self._create_users()
        tags = self._create_tags()
        blogs = self._create_blogs(users, tags)
        self._create_comments(users, blogs)
        self._create_social(users, blogs)

    def _create_users(self):
        specs = {
            'admin': ('Админ', 'Рупора', True),
            'alisa': ('Алиса', 'Смирнова', False),
            'timur': ('Тимур', 'Галеев', False),
            'maria': ('Мария', 'Орлова', False),
            'reader': ('Иван', 'Читатель', False),
        }
        users = {}
        for suffix, (first_name, last_name, is_staff) in specs.items():
            username = f'{self.namespace}_{suffix}'
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.test',
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': is_staff,
                    'is_superuser': is_staff,
                },
            )
            user.email = f'{username}@example.test'
            user.first_name = first_name
            user.last_name = last_name
            user.is_staff = is_staff
            user.is_superuser = is_staff
            user.set_password(PASSWORD)
            user.save()
            users[suffix] = user
        return users

    def _create_tags(self):
        legacy_specs = {
            'nature': ('Природа', '#219653'),
            'programming': ('Программирование', '#3867D6'),
            'family': ('Семья', '#D980FA'),
        }
        for slug, (name, color) in legacy_specs.items():
            Tag.objects.filter(slug=slug).update(name=name, color=color)

        specs = [
            ('ai', 'AI', '#2F80ED'),
            ('city', 'Город', '#00A8A8'),
            ('travel', 'Путешествия', '#F2994A'),
            ('ecology', 'Экология', '#27AE60'),
            ('food', 'Еда', '#EB5757'),
            ('health', 'Здоровье', '#9B51E0'),
            ('culture', 'Культура', '#F2C94C'),
            ('education', 'Образование', '#56CCF2'),
        ]
        tags = {}
        for slug, name, color in specs:
            tag, _ = Tag.objects.get_or_create(
                slug=f'{self.namespace}-{slug}',
                defaults={'name': name, 'color': color},
            )
            tag.name = name
            tag.color = color
            tag.save()
            tags[slug] = tag
        return tags

    def _create_blogs(self, users, tags):
        specs = [
            {
                'key': 'bike',
                'author': 'alisa',
                'name': 'Городские веломаршруты без спешки',
                'text': 'Подборка спокойных маршрутов через парки, набережные и тихие улицы. Подойдет для выходных и коротких поездок после работы.',
                'tags': ['city', 'ecology', 'travel'],
                'color': '#74B9FF',
                'embedding': [1.0, 0.0, 0.0, 0.0],
            },
            {
                'key': 'walk',
                'author': 'alisa',
                'name': 'Как выбрать тихий маршрут для прогулки',
                'text': 'Смотрим на шум, освещение, транспорт рядом и точки отдыха. Такой маршрут помогает восстановиться без долгой подготовки.',
                'tags': ['city', 'health'],
                'color': '#55EFC4',
                'embedding': [0.96, 0.08, 0.0, 0.0],
            },
            {
                'key': 'django',
                'author': 'timur',
                'name': 'Django REST Framework на практике',
                'text': 'Короткие заметки о viewsets, serializers, permissions и тестировании API. Хорошая база для дипломного проекта.',
                'tags': ['ai', 'education'],
                'color': '#A29BFE',
                'embedding': [0.0, 1.0, 0.0, 0.0],
            },
            {
                'key': 'ml',
                'author': 'timur',
                'name': 'Нейросети в блог-платформе',
                'text': 'Модерация текста, подбор тегов и поиск похожих публикаций делают платформу умнее и удобнее для автора.',
                'tags': ['ai', 'education'],
                'color': '#6C5CE7',
                'embedding': [0.0, 0.94, 0.05, 0.0],
            },
            {
                'key': 'soup',
                'author': 'maria',
                'name': 'Домашний суп после рабочей недели',
                'text': 'Простой рецепт с овощами, зеленью и понятным ритмом готовки. Подойдет, когда хочется теплой спокойной еды.',
                'tags': ['food', 'health'],
                'color': '#FAB1A0',
                'embedding': [0.0, 0.0, 1.0, 0.0],
            },
            {
                'key': 'breakfast',
                'author': 'maria',
                'name': 'Полезный завтрак без спешки',
                'text': 'Овсянка, ягоды, творог и немного орехов. Собирается быстро и держит энергию до обеда.',
                'tags': ['food', 'health'],
                'color': '#FF7675',
                'embedding': [0.0, 0.0, 0.92, 0.0],
            },
            {
                'key': 'museum',
                'author': 'alisa',
                'name': 'Маленькие музеи большого города',
                'text': 'Несколько камерных мест, где можно провести час, открыть новую тему и не устать от толпы.',
                'tags': ['city', 'culture'],
                'color': '#FDCB6E',
                'embedding': [0.65, 0.0, 0.0, 0.55],
            },
            {
                'key': 'volunteers',
                'author': 'timur',
                'name': 'Волонтерская уборка парка',
                'text': 'Как организовать небольшой городской субботник: роли, инвентарь, безопасность и пост с отчетом.',
                'tags': ['ecology', 'city'],
                'color': '#00B894',
                'embedding': [0.8, 0.0, 0.0, 0.2],
            },
            {
                'key': 'blocked',
                'author': 'maria',
                'name': 'Заблокированная демо-публикация',
                'text': 'Синтетический пример публикации, скрытой автоматической модерацией.',
                'tags': ['ai'],
                'color': '#B2BEC3',
                'status': 'blocked',
                'reason': 'Demo: публикация скрыта модерацией',
                'embedding': [0.9, 0.0, 0.1, 0.0],
            },
            {
                'key': 'pending',
                'author': 'maria',
                'name': 'Публикация ожидает проверки',
                'text': 'Синтетический пример статуса pending для демонстрации админской модерации.',
                'tags': ['ai', 'education'],
                'color': '#DFE6E9',
                'status': 'pending',
                'reason': None,
                'embedding': [0.2, 0.7, 0.0, 0.0],
            },
            {
                'key': 'bookclub',
                'author': 'alisa',
                'name': 'Книжный клуб во дворе',
                'text': 'Как собрать соседей на обсуждение книги: выбрать короткий текст, договориться о времени и оставить место для спора.',
                'tags': ['culture', 'education'],
                'color': '#E17055',
                'embedding': [0.1, 0.2, 0.0, 0.8],
            },
            {
                'key': 'garden',
                'author': 'timur',
                'name': 'Мини-сад на балконе',
                'text': 'Базилик, мята и томаты черри растут даже в небольшой квартире, если подобрать свет и регулярный полив.',
                'tags': ['ecology', 'food'],
                'color': '#81ECEC',
                'embedding': [0.45, 0.0, 0.45, 0.0],
            },
            {
                'key': 'river',
                'author': 'alisa',
                'name': 'Маршрут вдоль реки на вечер',
                'text': 'Набережная, несколько точек с видом на закат и короткая остановка у кофейни. Такой маршрут легко повторить после учебы или работы.',
                'tags': ['city', 'travel', 'health'],
                'color': '#0984E3',
                'embedding': [0.9, 0.04, 0.0, 0.15],
            },
            {
                'key': 'workshop',
                'author': 'timur',
                'name': 'Воркшоп по машинному обучению',
                'text': 'План открытого занятия: постановка задачи, подготовка данных, базовая модель и понятная демонстрация результата.',
                'tags': ['ai', 'education'],
                'color': '#5F27CD',
                'embedding': [0.0, 0.98, 0.02, 0.0],
            },
            {
                'key': 'market',
                'author': 'maria',
                'name': 'Сезонный рынок рядом с домом',
                'text': 'Как выбрать свежие овощи, зелень и ягоды, а заодно поддержать небольших производителей своего района.',
                'tags': ['food', 'city', 'ecology'],
                'color': '#EE5253',
                'embedding': [0.42, 0.0, 0.82, 0.0],
            },
            {
                'key': 'language',
                'author': 'alisa',
                'name': 'Как не бросить изучение языка',
                'text': 'Небольшие ежедневные практики, понятные цели и дружеская среда помогают учиться без ощущения бесконечного марафона.',
                'tags': ['education', 'health'],
                'color': '#54A0FF',
                'embedding': [0.02, 0.68, 0.0, 0.45],
            },
            {
                'key': 'cinema',
                'author': 'maria',
                'name': 'Киносеанс под открытым небом',
                'text': 'Дворовый показ фильма можно организовать без сложной техники: нужен экран, звук, пледы и спокойный вечер.',
                'tags': ['culture', 'city'],
                'color': '#F368E0',
                'embedding': [0.5, 0.0, 0.0, 0.72],
            },
            {
                'key': 'sleep',
                'author': 'timur',
                'name': 'Цифровая гигиена перед сном',
                'text': 'Отключаем лишние уведомления, переносим тяжелые задачи на утро и оставляем телефону место вне кровати.',
                'tags': ['health', 'education'],
                'color': '#576574',
                'embedding': [0.0, 0.36, 0.0, 0.78],
            },
        ]

        blogs = {}
        for spec in specs:
            blog, _ = Blog.objects.get_or_create(
                author=users[spec['author']],
                name=spec['name'],
                defaults={'text': spec['text']},
            )
            blog.text = spec['text']
            blog.moderation_status = spec.get('status', 'approved')
            blog.moderation_reason = spec.get('reason')
            blog.embedding = spec['embedding']
            self._set_demo_image(blog, spec['key'], spec['color'])
            blog.save()
            blog.tags.set([tags[tag_key] for tag_key in spec['tags']])
            blogs[spec['key']] = blog
        return blogs

    def _set_demo_image(self, blog, key, color):
        image = Image.new('RGB', (960, 640), color=color)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 960, 640), fill=color)
        draw.polygon((0, 0, 420, 0, 0, 360), fill='#FFFFFF')
        draw.polygon((960, 120, 960, 640, 520, 640), fill='#111827')
        draw.ellipse((620, 56, 1000, 436), outline='#FFFFFF', width=12)
        draw.ellipse((-140, 330, 260, 730), outline='#FFFFFF', width=10)
        draw.rectangle((0, 430, 960, 640), fill='#111827')
        draw.rectangle((48, 476, 138, 482), fill='#4A61DD')
        draw.text((48, 512), blog.name[:55], fill='#FFFFFF')
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        blog.image.save(
            f'{self.namespace}_{key}.png',
            ContentFile(buffer.getvalue()),
            save=False,
        )

    def _create_comments(self, users, blogs):
        specs = [
            ('reader', 'bike', 'Отличная подборка, хочу попробовать маршрут в субботу.', 'approved', None),
            ('timur', 'bike', 'Добавил бы еще карту с точками отдыха.', 'approved', None),
            ('maria', 'django', 'Полезно для раздела с API в диссертации.', 'approved', None),
            ('reader', 'ml', 'Похожий поиск действительно хорошо смотрится в демо.', 'approved', None),
            ('alisa', 'soup', 'Суп получился очень домашним, спасибо за идею.', 'approved', None),
            ('maria', 'river', 'Очень красивый маршрут для вечернего скриншота.', 'approved', None),
            ('reader', 'workshop', 'Такой формат хорошо объясняет пользу AI-модуля.', 'approved', None),
            ('timur', 'market', 'Можно добавить список сезонных продуктов по месяцам.', 'approved', None),
            ('reader', 'language', 'Забираю идею с маленькими ежедневными шагами.', 'approved', None),
            ('reader', 'bike', 'Скрытый демо-комментарий.', 'blocked', 'Demo: комментарий скрыт модерацией'),
            ('reader', 'walk', 'Комментарий ожидает проверки.', 'pending', None),
        ]
        for author_key, blog_key, text, status, reason in specs:
            Comment.objects.update_or_create(
                author=users[author_key],
                blog=blogs[blog_key],
                text=text,
                defaults={
                    'moderation_status': status,
                    'moderation_reason': reason,
                },
            )

    def _create_social(self, users, blogs):
        likes = [
            ('reader', 'bike'),
            ('reader', 'django'),
            ('reader', 'ml'),
            ('alisa', 'soup'),
            ('maria', 'bike'),
            ('timur', 'bookclub'),
            ('reader', 'river'),
            ('alisa', 'workshop'),
            ('timur', 'market'),
            ('maria', 'cinema'),
            ('reader', 'sleep'),
        ]
        favorites = [
            ('reader', 'bike'),
            ('reader', 'django'),
            ('alisa', 'garden'),
            ('maria', 'walk'),
            ('reader', 'language'),
            ('alisa', 'cinema'),
            ('timur', 'river'),
        ]
        subscriptions = [
            ('reader', 'alisa'),
            ('reader', 'timur'),
            ('alisa', 'maria'),
            ('maria', 'timur'),
        ]
        for user_key, blog_key in likes:
            Like.objects.get_or_create(user=users[user_key], blog=blogs[blog_key])
        for user_key, blog_key in favorites:
            Favourite.objects.get_or_create(user=users[user_key], blog=blogs[blog_key])
        for user_key, author_key in subscriptions:
            Subscribe.objects.get_or_create(
                user=users[user_key],
                author=users[author_key],
            )
