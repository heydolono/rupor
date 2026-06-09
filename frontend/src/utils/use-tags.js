import React from "react";

export function useTags() {
  const [ value, setValue ] = React.useState([])

  const handleChange = id => {
    setValue(prev => prev.map(item => (
      item.id === id ? { ...item, value: !item.value } : item
    )))
  }

  return { value, handleChange, setValue }
}
