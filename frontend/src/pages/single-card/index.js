// SingleCard.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useRouteMatch, useParams, useHistory } from 'react-router-dom';
import { Container, Main, Button, TagsContainer, Icons, LinkComponent } from '../../components';
import { UserContext, AuthContext } from '../../contexts';
import MetaTags from 'react-meta-tags';
import Description from './description';
import Comments from '../../components/Comments';
import CardList from '../../components/card-list';
import Card from '../../components/card';
import cn from 'classnames';
import styles from './styles.module.css';
import { useBlog } from '../../utils/index.js';
import api from '../../api';

const SingleCard = ({ loadItem, updateOrders }) => {
  const [loading, setLoading] = useState(true);
  const [similarBlogs, setSimilarBlogs] = useState([]);
  const { blog, setBlog, handleLike, handleSubscribe } = useBlog();
  const authContext = useContext(AuthContext);
  const userContext = useContext(UserContext);
  const { id } = useParams();
  const history = useHistory();

  useEffect(() => {
    api.getBlog({ blog_id: id })
      .then(res => {
        setBlog(res);
        setLoading(false);
      })
      .catch(() => {
        history.push('/rupor');
      });
  }, [id, history, setBlog]);

  useEffect(() => {
    api.getSimilarBlogs({ blog_id: id })
      .then(setSimilarBlogs)
      .catch(() => {});
  }, [id]);

  const { url } = useRouteMatch();
  const { author = {}, image, tags, name, text, is_favorited, moderation_status, moderation_reason } = blog;
  const isBlocked = moderation_status === 'blocked';
  const isAuthor = (userContext || {}).id === (author || {}).id;

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>{name}</title>
          <meta name="description" content={`Рупор - ${name}`} />
          <meta property="og:title" content={name} />
        </MetaTags>
        <div className={styles['single-card']}>
          <img src={image} alt={name} className={styles["single-card__image"]} />
          <div className={styles["single-card__info"]}>
            {isBlocked && isAuthor && (
              <div style={{
                background: '#ffebee', border: '1px solid #ef5350',
                borderRadius: '8px', padding: '12px 16px', marginBottom: '16px',
                color: '#c62828', fontWeight: 'bold'
              }}>
                Заблокировано нейросетью: {moderation_reason || 'причина не указана'}
              </div>
            )}
            {!isBlocked && (
              <div style={{
                background: '#e8f5e9', border: '1px solid #66bb6a',
                borderRadius: '8px', padding: '6px 12px', marginBottom: '16px',
                color: '#2e7d32', fontSize: '14px', display: 'inline-block', alignSelf: 'flex-start'
              }}>
                Проверено нейросетью
              </div>
            )}
            <div className={styles["single-card__header-info"]}>
              <h1 className={styles["single-card__title"]}>{name}</h1>
              {authContext && (
                <Button
                  modifier='style_none'
                  clickHandler={() => {
                    handleLike({ id, toLike: Number(!is_favorited) });
                  }}
                >
                  {is_favorited ? <Icons.StarBigActiveIcon /> : <Icons.StarBigIcon />}
                </Button>
              )}
            </div>
            <TagsContainer tags={tags} />
            <div>
              <p className={styles['single-card__text_with_link']}>
                <div className={styles['single-card__text']}>
                  <Icons.UserIcon /> <LinkComponent
                    title={`${author.first_name} ${author.last_name}`}
                    href={`/user/${author.id}`}
                    className={styles['single-card__link']}
                  />
                </div>
                {isAuthor && (
                  <LinkComponent
                    href={`${url}/edit`}
                    title='Редактировать'
                    className={styles['single-card__edit']}
                  />
                )}
              </p>
            </div>
            <div className={styles['single-card__buttons']}>
              {!isAuthor && authContext && (
                <Button
                  className={styles['single-card__button']}
                  modifier='style_light-blue'
                  clickHandler={() => {
                    handleSubscribe({ author_id: author.id, toSubscribe: !author.is_subscribed });
                  }}
                >
                  {author.is_subscribed ? 'Отписаться от автора' : 'Подписаться на автора'}
                </Button>
              )}
            </div>
            {!isBlocked && <Description description={text} />}
            {isBlocked && !isAuthor && (
              <p style={{ color: '#999', fontStyle: 'italic' }}>
                Этот пост заблокирован модерацией
              </p>
            )}
            <Comments blogId={id} authContext={authContext} />
            {similarBlogs.length > 0 && (
              <div style={{ marginTop: '40px' }}>
                <h2 style={{ fontFamily: 'Montserrat, sans-serif', fontSize: '24px' }}>
                  Похожие записи
                </h2>
                <p style={{ fontSize: '13px', color: '#666', marginTop: '-8px', marginBottom: '16px' }}>
                  Найдено нейросетью по смыслу текста
                </p>
                <CardList>
                  {similarBlogs.map(card => (
                    <Card {...card} key={card.id} />
                  ))}
                </CardList>
              </div>
            )}
          </div>
        </div>
      </Container>
    </Main>
  );
};

export default SingleCard;
