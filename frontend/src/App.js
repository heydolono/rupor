import logo from './logo.svg';
import './App.css';
import { Switch, Route, useHistory, Redirect, useLocation } from 'react-router-dom'
import React, { useState, useEffect } from 'react'
import { Header, Footer, ProtectedRoute } from './components'
import api from './api'
import styles from './styles.module.css'
import cn from 'classnames'
import hamburgerImg from './images/hamburger-menu.png'

import {
  Main,
  SignIn,
  Subscriptions,
  Favorites,
  SingleCard,
  SignUp,
  BlogEdit,
  BlogCreate,
  User,
  ChangePassword
} from './pages'

import { AuthContext, UserContext } from './contexts'

function App() {
  const [ loggedIn, setLoggedIn ] = useState(null)
  const [ user, setUser ] = useState({})
  const [ menuToggled, setMenuToggled ] = useState(false)

  const registration = ({
    email,
    password,
    username,
    first_name,
    last_name
  }) => {
    api.signup({ email, password, username, first_name, last_name })
      .then(res => {
        history.push('/signin')
      })
      .catch(err => {
        const errors = Object.values(err)
        if (errors) {
          alert(errors.join(', '))
        }
        setLoggedIn(false)
      })
  }

  const changePassword = ({
    new_password,
    current_password
  }) => {
    api.changePassword({ new_password, current_password })
      .then(res => {
        history.push('/signin')
      })
      .catch(err => {
        const errors = Object.values(err)
        if (errors) {
          alert(errors.join(', '))
        }
      })
  }

  const authorization = ({
    email, password
  }) => {
    api.signin({
      email, password
    }).then(res => {
      if (res.auth_token) {
        localStorage.setItem('token', res.auth_token)
        api.getUserData()
          .then(res => {
            setUser(res)
            setLoggedIn(true)
          })
          .catch(err => {
            setLoggedIn(false)
            history.push('/signin')
          })
      } else {
        setLoggedIn(false)
      }
    })
    .catch(err => {
      const errors = Object.values(err)
      if (errors) {
        alert(errors.join(', '))
      }
      setLoggedIn(false)
    })
  }

  const loadSingleItem = ({ id, callback }) => {
    setTimeout(_ => {
      callback()
    }, 3000)
  }

  const history = useHistory()
  const onSignOut = () => {
    api
      .signout()
      .then(res => {
        localStorage.removeItem('token')
        setLoggedIn(false)
      })
      .catch(err => {
        const errors = Object.values(err)
        if (errors) {
          alert(errors.join(', '))
        }
      })
  }

  useEffect(_ => {
    if (loggedIn) {
    }
  }, [loggedIn])

  useEffect(_ => {
    const token = localStorage.getItem('token')
    if (token) {
      return api.getUserData()
        .then(res => {
          setUser(res)
          setLoggedIn(true)
        })
        .catch(err => {
          setLoggedIn(false)
          history.push('/signin')
        })
    }
    setLoggedIn(false)
  }, [])

  if (loggedIn === null) {
    return <div className={styles.loading}>Loading!!</div>
  }
  
  return <AuthContext.Provider value={loggedIn}>
    <UserContext.Provider value={user}>
      <div className={cn("App", {
        [styles.appMenuToggled]: menuToggled
      })}>
        <div
          className={styles.menuButton}
          onClick={_ => setMenuToggled(!menuToggled)}
        >
          <img src={hamburgerImg} />
        </div>
        <Header loggedIn={loggedIn} onSignOut={onSignOut} />
        <Switch>
          <ProtectedRoute
            exact
            path='/user/:id'
            component={User}
            loggedIn={loggedIn}
          />
          <ProtectedRoute
            exact
            path='/subscriptions'
            component={Subscriptions}
            loggedIn={loggedIn}
          />
          <ProtectedRoute
            exact
            path='/favorites'
            component={Favorites}
            loggedIn={loggedIn}
          />
          <ProtectedRoute
            exact
            path='/rupor/create'
            component={BlogCreate}
            loggedIn={loggedIn}
          />

          <ProtectedRoute
            exact
            path='/rupor/:id/edit'
            component={BlogEdit}
            loggedIn={loggedIn}
            loadItem={loadSingleItem}
          />
          <ProtectedRoute
            exact
            path='/change-password'
            component={ChangePassword}
            loggedIn={loggedIn}
            onPasswordChange={changePassword}
          />

          <Route
            exact
            path='/rupor/:id'
          >
            <SingleCard
              loggedIn={loggedIn}
              loadItem={loadSingleItem}
            />
          </Route>

          <Route exact path='/rupor'>
            <Main
            />
          </Route>


          <Route exact path='/signin'>
            <SignIn
              onSignIn={authorization}
            />
          </Route>
          <Route exact path='/signup'>
            <SignUp
              onSignUp={registration}
            />
          </Route>
          <Route path='/'>
            {loggedIn ? <Redirect to='/rupor' /> : <Redirect to='/signin'/>}
          </Route>
        </Switch>
        <Footer />
      </div>
    </UserContext.Provider>
  </AuthContext.Provider>
}

export default App;
