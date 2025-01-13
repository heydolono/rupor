// Comments.jsx
import React, { useState, useEffect } from 'react';
import api from '../../api';
import { Container, Textarea2, Button } from '../../components';
import styles from './styles.module.css';

function Comments({ blogId, authContext }) {
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getComments({ blog_id: blogId })
            .then(setComments)
            .catch(error => {
                console.error("Error fetching comments:", error);
            })
            .finally(() => setLoading(false));
    }, [blogId]);

    const handleAddComment = () => {
        if (!newComment) return;
        api.addComment({ blog_id: blogId, text: newComment })
            .then(comment => {
                setComments([...comments, comment]);
                setNewComment('');
            })
            .catch(error => {
                console.error("Error adding comment:", error);
            });
    };

    return (
        <div className={styles.commentsWrapper}>
            <h3>Комментарии</h3>
            {loading ? (
                <p>Загрузка комментариев</p>
            ) : (
                <div className={styles.commentsList}>
                    {comments.map(comment => (
                        <div key={comment.id} className={styles.commentItem}>
                            <p>{comment.text}</p>
                        </div>
                    ))}
                </div>
            )}
            {authContext && (
                <div className={styles.commentForm}>
                    <Textarea2
                        className={styles.commentTextarea}
                        value={newComment}
                        onChange={e => setNewComment(e.target.value)}
                        placeholder="Введите ваш комментарий"
                    />
                    <button className={styles.commentButton} onClick={handleAddComment}>
                        Добавить комментарий
                    </button>
                </div>
            )}
        </div>
    );
}

export default Comments;
