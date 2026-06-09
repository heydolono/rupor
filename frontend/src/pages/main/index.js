import { Card, Title, Pagination, CardList, Container, Main, CheckboxGroup  } from '../../components'
import styles from './styles.module.css'
import { useBlogs } from '../../utils/index.js'
import { useEffect } from 'react'
import api from '../../api'
import MetaTags from 'react-meta-tags'

const HomePage = ({ updateOrders }) => {
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
    handleLike
  } = useBlogs()


  const getBlogs = ({ page = 1, tags }) => {
    api
      .getBlogs({ page, tags })
      .then(res => {
        const { results, count } = res
        setBlogs(results)
        setBlogsCount(count)
      })
  }

  useEffect(_ => {
    getBlogs({ page: blogsPage, tags: tagsValue })
  }, [blogsPage, tagsValue])

  useEffect(_ => {
    api.getTags()
      .then(tags => {
        setTagsValue(tags.map(tag => ({ ...tag, value: true })))
      })
  }, [])


  return <Main>
    <Container>
      <MetaTags>
        <title>Рупор</title>
        <meta name="description" content="Лента" />
        <meta property="og:title" content="Лента" />
      </MetaTags>
      <div className={styles.title}>
        <Title title='Лента' />
      </div>
      <div className={styles.filters}>
        <CheckboxGroup
          className={styles.filterGroup}
          values={tagsValue}
          handleChange={value => {
            setBlogsPage(1)
            handleTagsChange(value)
          }}
        />
      </div>
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

export default HomePage
