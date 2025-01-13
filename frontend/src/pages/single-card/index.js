// SingleCard.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useRouteMatch, useParams, useHistory } from 'react-router-dom';
import { Container, Main, Button, TagsContainer, Icons, LinkComponent } from '../../components';
import { UserContext, AuthContext } from '../../contexts';
import MetaTags from 'react-meta-tags';
import Description from './description';
import Comments from '../../components/Comments';
import cn from 'classnames';
import styles from './styles.module.css';
import { useBlog } from '../../utils/index.js';
import api from '../../api';

const SingleCard = ({ loadItem, updateOrders }) => {
  const [loading, setLoading] = useState(true);
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

  const { url } = useRouteMatch();
  const { author = {}, image, tags, name, text, is_favorited } = blog;

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
                {(userContext || {}).id === author.id && (
                  <LinkComponent
                    href={`${url}/edit`}
                    title='Редактировать'
                    className={styles['single-card__edit']}
                  />
                )}
              </p>
            </div>
            <div className={styles['single-card__buttons']}>
              {(userContext || {}).id !== author.id && authContext && (
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
            <Description description={text} />
            <Comments blogId={id} authContext={authContext} />
          </div>
        </div>
      </Container>
    </Main>
  );
};

export default SingleCard;
