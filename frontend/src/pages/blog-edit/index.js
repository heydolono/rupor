import { Container, Input, Title, CheckboxGroup, Main, Form, Button, Textarea, FileInput } from '../../components';
import styles from './styles.module.css';
import api from '../../api';
import { useEffect, useState } from 'react';
import { useTags } from '../../utils';
import { useParams, useHistory } from 'react-router-dom';
import MetaTags from 'react-meta-tags';

const BlogEdit = ({ onItemDelete }) => {
  const { value, handleChange, setValue } = useTags();
  const [blogName, setBlogName] = useState('');
  const [blogText, setBlogText] = useState('');
  const [blogFile, setBlogFile] = useState(null);
  const [blogFileWasManuallyChanged, setBlogFileWasManuallyChanged] = useState(false);
  const [loading, setLoading] = useState(true);
  const history = useHistory();
  const { id } = useParams();

  useEffect(() => {
    api.getTags().then(tags => {
      setValue(tags.map(tag => ({ ...tag, value: true })));
    });
  }, []);

  useEffect(() => {
    if (value.length === 0 || !loading) { return; }
    api.getBlog({ blog_id: id }).then(res => {
      const { image, tags, name, text } = res;
      setBlogText(text);
      setBlogName(name);
      setBlogFile(image);

      const tagsValueUpdated = value.map(item => {
        item.value = Boolean(tags.find(tag => tag.id === item.id));
        return item;
      });
      setValue(tagsValueUpdated);
      setLoading(false);
    }).catch(err => {
      history.push('/rupor');
    });
  }, [value]);

  const checkIfDisabled = () => {
    return (
      blogText === '' ||
      blogName === '' ||
      value.filter(item => item.value).length === 0 ||
      blogFile === '' ||
      blogFile === null
    );
  };

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Редактирование</title>
          <meta name="description" content="Рупор - Редактирование" />
          <meta property="og:title" content="Редактирование" />
        </MetaTags>
        <Title title='Редактирование' />
        <Form
          className={styles.form}
          onSubmit={e => {
            e.preventDefault();
            const data = {
              text: blogText,
              name: blogName,
              tags: value.filter(item => item.value).map(item => item.id),
              image: blogFile,
              blog_id: id
            };
            api.updateBlog(data, blogFileWasManuallyChanged)
              .then(res => {
                history.push(`/rupor/${id}`);
              })
              .catch(err => {
                const { non_field_errors } = err;
                if (non_field_errors) {
                  return alert(non_field_errors.join(', '));
                }
                const errors = Object.values(err);
                if (errors) {
                  alert(errors.join(', '));
                }
              });
          }}
        >
          <Input
            label='Название'
            value={blogName}
            onChange={e => setBlogName(e.target.value)}
          />
          <CheckboxGroup
            label='Теги'
            values={value}
            className={styles.checkboxGroup}
            labelClassName={styles.checkboxGroupLabel}
            tagsClassName={styles.checkboxGroupTags}
            checkboxClassName={styles.checkboxGroupItem}
            handleChange={handleChange}
          />
          <Textarea
            label='Текст'
            value={blogText}
            onChange={e => setBlogText(e.target.value)}
          />
          <FileInput
            onChange={file => {
              setBlogFileWasManuallyChanged(true);
              setBlogFile(file);
            }}
            className={styles.fileInput}
            label='Загрузить фото'
            file={blogFile}
          />
          <div className={styles.actions}>
            <Button
              modifier='style_dark-blue'
              disabled={checkIfDisabled()}
              className={styles.button}
            >
              Редактировать
            </Button>
            <div
              className={styles.deleteBlog}
              onClick={() => {
                api.deleteBlog({ blog_id: id })
                  .then(res => {
                    onItemDelete && onItemDelete();
                    history.push('/rupor');
                  });
              }}
            >
              Удалить
            </div>
          </div>
        </Form>
      </Container>
    </Main>
  );
};

export default BlogEdit;
