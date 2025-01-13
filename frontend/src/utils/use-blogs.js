import React, { useState } from "react";
import { useTags } from './index.js'
import api from '../api'

export default function useBlogs () {
  const [ blogs, setBlogs ] = useState([])
  const [ blogsCount, setBlogsCount ] = useState(0)
  const [ blogsPage, setBlogsPage ] = useState(1)
  const { value: tagsValue, handleChange: handleTagsChange, setValue: setTagsValue } = useTags()

  const handleLike = ({ id, toLike = true }) => {
    const method = toLike ? api.addToFavorites.bind(api) : api.removeFromFavorites.bind(api)
    method({ id }).then(res => {
      const blogsUpdated = blogs.map(blog => {
        if (blog.id === id) {
          blog.is_favorited = toLike
        }
        return blog
      })
      setBlogs(blogsUpdated)
    })
    .catch(err => {
      const { errors } = err
      if (errors) {
        alert(errors)
      }
    })
  }

  return {
    blogs,
    setBlogs,
    blogsCount,
    setBlogsCount,
    blogsPage,
    setBlogsPage,
    tagsValue,
    handleLike,
    handleTagsChange,
    setTagsValue
  }
}
