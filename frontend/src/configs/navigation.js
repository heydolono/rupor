export default [
  {
    title: 'Лента',
    href: '/rupor',
    auth: false
  },{
    title: 'Мои подписки',
    href: '/subscriptions',
    auth: true
  },{
    title: 'Поделиться',
    href: '/rupor/create',
    auth: true
  },{
    title: 'Избранное',
    href: '/favorites',
    auth: true
  },{
    title: 'Профиль',
    href: '/user/${user.id}',
    auth: true
  }
]
