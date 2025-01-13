// src/components/Nav/index.js
import React, { useState, useEffect } from 'react';
import styles from './style.module.css';
import cn from 'classnames';
import { LinkComponent } from '../index';
import navigation from '../../configs/navigation';
import api from '../../api'; 

const Nav = ({ loggedIn, orders }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (loggedIn) {
      api.getUserData()
        .then(data => setUser(data))
        .catch(err => console.error('Error fetching user data:', err));
    }
  }, [loggedIn]);

  const navItems = navigation.map(item => {
    if (!loggedIn && item.auth) {
      return null;
    }

    let href = item.href;
    if (user && item.href.includes('${user.id}')) {
      href = item.href.replace('${user.id}', user.id);
    }

    return (
      <li
        className={cn(styles.nav__item, {
          [styles.nav__item_active]: false
        })}
        key={href}
      >
        <LinkComponent
          title={item.title}
          activeClassName={styles.nav__link_active}
          href={href}
          exact
          className={styles.nav__link}
        />
        {item.href === '/cart' && orders > 0 && (
          <span className={styles['orders-count']}>{orders}</span>
        )}
      </li>
    );
  });

  return (
    <nav className={styles.nav}>
      <div className={styles.nav__container}>
        <ul className={styles.nav__items}>{navItems}</ul>
      </div>
    </nav>
  );
};

export default Nav;
