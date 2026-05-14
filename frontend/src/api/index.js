class Api {
  constructor (url, headers) {
    this._url = url
    this._headers = headers
  }

  checkResponse (res) {
    return new Promise((resolve, reject) => {
      if (res.status === 204) {
        return resolve(res)
      }
      const func = res.status < 400 ? resolve : reject
      res.json().then(data => func(data))
    })
  }

  signin ({ email, password }) {
    return fetch(
      '/api/auth/token/login/',
      {
        method: 'POST',
        headers: this._headers,
        body: JSON.stringify({
          email, password
        })
      }
    ).then(this.checkResponse)
  }

  signout () {
    const token = localStorage.getItem('token')
    return fetch(
      '/api/auth/token/logout/',
      {
        method: 'POST',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  signup ({ email, password, username, first_name, last_name }) {
    return fetch(
      `/api/users/`,
      {
        method: 'POST',
        headers: this._headers,
        body: JSON.stringify({
          email, password, username, first_name, last_name
        })
      }
    ).then(this.checkResponse)
  }

  getUserData () {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/users/me/`,
      {
        method: 'GET',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  changePassword ({ current_password, new_password }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/users/set_password/`,
      {
        method: 'POST',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        },
        body: JSON.stringify({ current_password, new_password })
      }
    ).then(this.checkResponse)
  }


  // blogs

  getBlogs ({
    page = 1,
    limit = 6,
    is_favorited = 0,
    is_liked = 0,
    author,
    tags
  } = {}) {
      const token = localStorage.getItem('token')
      const authorization = token ? { 'authorization': `Token ${token}` } : {}
      const tagsString = tags ? tags.filter(tag => tag.value).map(tag => `&tags=${tag.slug}`).join('') : ''
      return fetch(
        `/api/blog/?page=${page}&limit=${limit}${author ? `&author=${author}` : ''}${is_favorited ? `&is_favorited=${is_favorited}` : ''}${is_liked ? `&is_liked=${is_liked}` : ''}${tagsString}`,
        {
          method: 'GET',
          headers: {
            ...this._headers,
            ...authorization
          }
        }
      ).then(this.checkResponse)
  }

  getBlog ({
    blog_id
  }) {
    const token = localStorage.getItem('token')
    const authorization = token ? { 'authorization': `Token ${token}` } : {}
    return fetch(
      `/api/blog/${blog_id}/`,
      {
        method: 'GET',
        headers: {
          ...this._headers,
          ...authorization
        }
      }
    ).then(this.checkResponse)
  }

  createBlog ({
    name = '',
    image,
    tags = [],
    text = ''
  }) {
    const token = localStorage.getItem('token')
    return fetch(
      '/api/blog/',
      {
        method: 'POST',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        },
        body: JSON.stringify({
          name,
          image,
          tags,
          text
        })
      }
    ).then(this.checkResponse)
  }

  updateBlog ({
    name,
    blog_id,
    image,
    tags,
    text
  }, wasImageUpdated) { // image was changed
    const token = localStorage.getItem('token')
    return fetch(
      `/api/blog/${blog_id}/`,
      {
        method: 'PATCH',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        },
        body: JSON.stringify({
          name,
          id: blog_id,
          image: wasImageUpdated ? image : undefined,
          tags,
          text
        })
      }
    ).then(this.checkResponse)
  }

  addToFavorites ({ id }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/blog/${id}/favorite/`,
      {
        method: 'POST',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  removeFromFavorites ({ id }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/blog/${id}/favorite/`,
      {
        method: 'DELETE',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  getUser ({ id }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/users/${id}/`,
      {
        method: 'GET',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  getUsers ({
    page = 1,
    limit = 6
  }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/users/?page=${page}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  // subscriptions

  getSubscriptions ({
    page, 
    limit = 6,
    blog_limit = 3
  }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/users/subscriptions/?page=${page}&limit=${limit}&blog_limit=${blog_limit}`,
      {
        method: 'GET',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  deleteSubscriptions ({
    author_id
  }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/users/${author_id}/subscribe/`,
      {
        method: 'DELETE',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  subscribe ({
    author_id
  }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/users/${author_id}/subscribe/`,
      {
        method: 'POST',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  // similar
  getSimilarBlogs ({ blog_id }) {
    const token = localStorage.getItem('token')
    const authorization = token ? { 'authorization': `Token ${token}` } : {}
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 10000)
    return fetch(
      `/api/blog/${blog_id}/similar/`,
      {
        method: 'GET',
        headers: { ...this._headers, ...authorization },
        signal: controller.signal
      }
    ).then(res => {
      clearTimeout(timeout)
      return this.checkResponse(res)
    }).catch(err => {
      clearTimeout(timeout)
      throw err
    })
  }

  // tags
  getTags () {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/tags/`,
      {
        method: 'GET',
        headers: {
          ...this._headers
        }
      }
    ).then(this.checkResponse)
  }

  suggestTags ({ name, text }) {
    const token = localStorage.getItem('token')
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 15000)
    return fetch(
      `/api/blog/suggest_tags/`,
      {
        method: 'POST',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        },
        body: JSON.stringify({ name, text }),
        signal: controller.signal
      }
    ).then(res => {
      clearTimeout(timeout)
      return this.checkResponse(res)
    }).catch(err => {
      clearTimeout(timeout)
      throw err
    })
  }

  deleteBlog ({ blog_id }) {
    const token = localStorage.getItem('token')
    return fetch(
      `/api/blog/${blog_id}/`,
      {
        method: 'DELETE',
        headers: {
          ...this._headers,
          'authorization': `Token ${token}`
        }
      }
    ).then(this.checkResponse)
  }

  addLike({ id }) {
    const token = localStorage.getItem('token');
    return fetch(`/api/blog/${id}/like/`, {
      method: 'POST',
      headers: {
        ...this._headers,
        'authorization': `Token ${token}`
      }
    }).then(this.checkResponse);
  }

  removeLike({ id }) {
    const token = localStorage.getItem('token');
    return fetch(`/api/blog/${id}/like/`, {
      method: 'DELETE',
      headers: {
        ...this._headers,
        'authorization': `Token ${token}`
      }
    }).then(this.checkResponse);
  }

  // comments
  getComments({ blog_id }) {
    return fetch(`/api/blog/${blog_id}/comments/`, {
      method: 'GET',
      headers: this._headers
    }).then(this.checkResponse);
  }

  addComment({ blog_id, text }) {
    const token = localStorage.getItem('token');
    return fetch(`/api/blog/${blog_id}/comment/`, {
      method: 'POST',
      headers: {
        ...this._headers,
        'authorization': `Token ${token}`
      },
      body: JSON.stringify({ text })
    }).then(this.checkResponse);
  }
}

export default new Api(process.env.API_URL || 'http://localhost', { 'content-type': 'application/json' })
