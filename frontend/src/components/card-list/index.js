import styles from './style.module.css'
import cn from 'classnames'


const CardList = ({ children, className }) => {
  return <div className={cn(styles.cardList, className)}>
    {children}
  </div>
}

export default CardList
