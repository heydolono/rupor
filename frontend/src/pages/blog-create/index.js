import { Container, Input, Title, CheckboxGroup, Main, Form, Button, Textarea, FileInput } from '../../components';
import styles from './styles.module.css';
import api from '../../api';
import { useEffect, useState } from 'react';
import { useTags } from '../../utils';
import { useHistory } from 'react-router-dom';
import MetaTags from 'react-meta-tags';

const BlogCreate = ({ onEdit }) => {
  const { value, handleChange, setValue } = useTags();
  const [blogName, setBlogName] = useState('');
  const history = useHistory();
  const [blogText, setBlogText] = useState('');
  const [blogFile, setBlogFile] = useState(null);

  useEffect(() => {
    api.getTags()
      .then(tags => {
        setValue(tags.map(tag => ({ ...tag, value: true })));
      });
  }, []);

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
          <title>Поделиться</title>
          <meta name="description" content="Рупор - Поделиться" />
          <meta property="og:title" content="Поделиться" />
        </MetaTags>
        <Title title='Поделиться' />
        <Form
          className={styles.form}
          onSubmit={e => {
            e.preventDefault();
            const data = {
              text: blogText,
              name: blogName,
              tags: value.filter(item => item.value).map(item => item.id),
              image: blogFile
            };
            api.createBlog(data)
              .then(res => {
                history.push(`/rupor/${res.id}`);
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
            onChange={e => setBlogText(e.target.value)}
          />
          <FileInput
            onChange={file => setBlogFile(file)}
            className={styles.fileInput}
            label='Загрузить фото'
          />
          <Button
            modifier='style_dark-blue'
            disabled={checkIfDisabled()}
            className={styles.button}
          >
            Создать
          </Button>
        </Form>
      </Container>
    </Main>
  );
};

export default BlogCreate;
