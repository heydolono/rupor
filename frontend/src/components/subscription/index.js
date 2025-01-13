import styles from './styles.module.css'
import { Icons, Button, LinkComponent } from '../index'

const countForm = (number, titles) => {
  number = Math.abs(number);
  if (Number.isInteger(number)) {
    let cases = [2, 0, 1, 1, 1, 2];  
    return titles[(number % 100 > 4 && number % 100 < 20) ? 2 : cases[(number % 10 < 5) ? number % 10 : 5]];
  }
  return titles[1];
}

const Subscription = ({ email, first_name, last_name, username, removeSubscription, blog_count, id, blog }) => {
  const shouldShowButton = blog_count > 3;
  const moreBlog = blog_count - 3;
  return (
    <div className={styles.subscription}>
      <div className={styles.subscriptionHeader}>
        <h2 className={styles.subscriptionTitle}>
          <LinkComponent className={styles.subscriptionRecipeLink} href={`/user/${id}`} title={`${first_name} ${last_name}`} />
        </h2>
      </div>
      <div className={styles.subscriptionBody}>
        <ul className={styles.subscriptionItems}>
          {blog.map(blog => (
            <li className={styles.subscriptionItem} key={blog.id}>
              <LinkComponent className={styles.subscriptionRecipeLink} href={`/rupor/${blog.id}`} title={
                <div className={styles.subscriptionRecipe}>
                  <img src={blog.image} alt={blog.name} className={styles.subscriptionRecipeImage} />
                  <h3 className={styles.subscriptionRecipeTitle}>
                    {blog.name}
                  </h3>
                </div>
              } />
            </li>
          ))}
          {shouldShowButton && (
            <li className={styles.subscriptionMore}>
              <LinkComponent
                className={styles.subscriptionLink}
                title={`Еще ${moreBlog} ${countForm(moreBlog, ['пост', 'поста', 'постов'])}...`}
                href={`/user/${id}`}
              />
            </li>
          )}
        </ul>
      </div>
      <div className={styles.subscriptionFooter}>
        <Button
          className={styles.subscriptionButton}
          clickHandler={_ => {
            removeSubscription({ id })
          }}
        >
          Отписаться
        </Button>
      </div>
    </div>
  );
}

export default Subscription;
