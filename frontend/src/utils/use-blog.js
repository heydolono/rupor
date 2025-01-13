import React, { useState } from "react";
import api from '../api'

export default function useBlog () {
  const [ blog, setBlog ] = useState({})

  const handleLike = ({ id, toLike = 1 }) => {
    const method = toLike ? api.addToFavorites.bind(api) : api.removeFromFavorites.bind(api)
    method({ id }).then(res => {
      const blogUpdated = { ...blog, is_favorited: Number(toLike) }
      setBlog(blogUpdated)
    })
    .catch(err => {
      const { errors } = err
      if (errors) {
        alert(errors)
      }
    })
  }

  const handleSubscribe = ({ author_id, toSubscribe = 1 }) => {
    const method = toSubscribe ? api.subscribe.bind(api) : api.deleteSubscriptions.bind(api)
      method({
        author_id
      })
      .then(_ => {
        const blogUpdated = { ...blog, author: { ...blog.author, is_subscribed: toSubscribe } }
        setBlog(blogUpdated)
      })
      .catch(err => {
        const { errors } = err
        if (errors) {
          alert(errors)
        }
      })
  }

  return {
    blog,
    setBlog,
    handleLike,
    handleSubscribe
  }
}
