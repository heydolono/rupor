import styles from './style.module.css';
import { LinkComponent, Icons, Button, TagsContainer } from '../index';
import { useContext, useState } from 'react';
import { AuthContext } from '../../contexts';
import Api from '../../api';

const Card = ({
  name = 'Без названия',
  id,
  image,
  is_favorited,
  is_liked,
  tags,
  author = {},
  handleLike,
  text = '',
  likes_count = 0,
  moderation_status
}) => {
  const isBlocked = moderation_status === 'blocked';
  const authContext = useContext(AuthContext);
  const [favorited, setFavorited] = useState(is_favorited);
  const [liked, setLiked] = useState(is_liked);
  const [likesCount, setLikesCount] = useState(likes_count);

  const handleLikeClick = () => {
    if (liked) {
      Api.removeLike({ id })
        .then(() => {
          setLiked(false);
          setLikesCount(likesCount - 1);
        })
        .catch(error => {
          console.error('Error removing like:', error);
        });
    } else {
      Api.addLike({ id })
        .then(() => {
          setLiked(true);
          setLikesCount(likesCount + 1);
        })
        .catch(error => {
          console.error('Error adding like:', error);
        });
    }
  };

  const handleFavoriteClick = () => {
    if (favorited) {
      Api.removeFromFavorites({ id })
        .then(() => {
          setFavorited(false);
        })
        .catch(error => {
          console.error('Error removing from favorites:', error);
        });
    } else {
      Api.addToFavorites({ id })
        .then(() => {
          setFavorited(true);
        })
        .catch(error => {
          console.error('Error adding to favorites:', error);
        });
    }
  };

  const truncateText = (text, limit = 250) => {
    if (text.length > limit) {
      return text.slice(0, limit) + '...';
    }
    return text;
  };

  return (
    <div className={styles.card}>
      <LinkComponent
        className={styles.card__title}
        href={`/rupor/${id}`}
        title={<div className={styles.card__image} style={{ backgroundImage: `url(${image})` }} />}
      />
        <div className={styles.card__body}>
          {isBlocked && (
            <span style={{
              background: '#ffebee', color: '#c62828', fontSize: '12px',
              padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold',
              marginBottom: '8px', display: 'inline-block'
            }}>
              Заблокировано
            </span>
          )}
          <LinkComponent
            className={styles.card__title}
            href={`/rupor/${id}`}
            title={name}
          />
        <TagsContainer tags={tags} />
        <div className={styles.card__text}>
          {truncateText(text)}
        </div>
        <div className={styles.card__author}>
          <Icons.UserIcon />
          <LinkComponent
            href={`/user/${author.id}`}
            title={`${author.first_name} ${author.last_name}`}
            className={styles.card__link}
          />
        </div>
      </div>

      <div className={styles.card__footer}>
        {authContext && (
          <>
            <Button
              modifier='style_none'
              clickHandler={handleFavoriteClick}
            >
              {favorited ? <Icons.StarActiveIcon /> : <Icons.StarIcon />}
            </Button>
            <div className={styles.likes_container}>
              <span className={styles.likes_count}>{likesCount}</span>
              <Button
                modifier='style_none'
                clickHandler={handleLikeClick}
              >
                {liked ? <Icons.HeartFilledIcon /> : <Icons.HeartIcon />}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Card;
