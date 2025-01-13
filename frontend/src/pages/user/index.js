import {
  Card,
  Title,
  Pagination,
  CardList,
  Button,
  CheckboxGroup,
  Container,
  Main 
} from '../../components'
import cn from 'classnames'
import styles from './styles.module.css'
import { useBlogs } from '../../utils/index.js'
import { useEffect, useState, useContext } from 'react'
import api from '../../api'
import { useParams, useHistory } from 'react-router-dom'
import { UserContext } from '../../contexts'
import MetaTags from 'react-meta-tags'

const UserPage = ({ updateOrders }) => {
  const {
    blogs,
    setBlogs,
    blogsCount,
    setBlogsCount,
    blogsPage,
    setBlogsPage,
    tagsValue,
    setTagsValue,
    handleTagsChange,
    handleLike,
  } = useBlogs()
  const { id } = useParams()
  const [ user, setUser ] = useState(null)
  const [ subscribed, setSubscribed ] = useState(false)
  const history = useHistory()
  const userContext = useContext(UserContext)

  const getBlogs = ({ page = 1, tags }) => {
    api
      .getBlogs({ page, author: id, tags })
        .then(res => {
          const { results, count } = res
          setBlogs(results)
          setBlogsCount(count)
        })
  }

  const getUser = () => {
    api.getUser({ id })
      .then(res => {
        setUser(res)
        setSubscribed(res.is_subscribed)
      })
      .catch(err => {
        history.push('/rupor')
      })
  }

  useEffect(_ => {
    if (!user) { return }
    getBlogs({ page: blogsPage, tags: tagsValue, author: user.id })
  }, [ blogsPage, tagsValue, user ])

  useEffect(_ => {
    getUser()
  }, [])

  useEffect(_ => {
    api.getTags()
      .then(tags => {
        setTagsValue(tags.map(tag => ({ ...tag, value: true })))
      })
  }, [])


  return <Main>
    <Container className={styles.container}>
      <MetaTags>
        <title>{user ? `${user.first_name} ${user.last_name}` : 'Страница пользователя'}</title>
        <meta name="description" content={user ? `Рупор - ${user.first_name} ${user.last_name}` : 'Рупор - Страница пользователя'} />
        <meta property="og:title" content={user ? `${user.first_name} ${user.last_name}` : 'Страница пользователя'} />
      </MetaTags>
      <div className={styles.title}>
        <Title
          className={cn({
            [styles.titleText]: (userContext || {}).id !== (user || {}).id
          })}
          title={user ? `${user.first_name} ${user.last_name}` : ''}
        />
        <CheckboxGroup
          values={tagsValue}
          handleChange={value => {
            setBlogsPage(1)
            handleTagsChange(value)
          }}
        />
      </div>
      {(userContext || {}).id !== (user || {}).id && <Button
        className={styles.buttonSubscribe}
        clickHandler={_ => {
          const method = subscribed ? api.deleteSubscriptions.bind(api) : api.subscribe.bind(api) 
            method({
              author_id: id
            })
            .then(_ => {
              setSubscribed(!subscribed)
            })
        }}
      >
        {subscribed ? 'Отписаться от автора' : 'Подписаться на автора'}
      </Button>}
      <CardList>
        {blogs.map(card => <Card
          {...card}
          key={card.id}
          handleLike={handleLike}
        />)}
      </CardList>
      <Pagination
        count={blogsCount}
        limit={6}
        page={blogsPage}
        onPageChange={page => setBlogsPage(page)}
      />
    </Container>
  </Main>
}

export default UserPage

