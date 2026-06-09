import { Container, Input, Title, CheckboxGroup, Main, Form, Button, Textarea, FileInput } from '../../components';
import styles from './styles.module.css';
import api from '../../api';
import { useEffect, useState, useRef } from 'react';
import { useTags } from '../../utils';
import { useHistory } from 'react-router-dom';
import MetaTags from 'react-meta-tags';

const BlogCreate = ({ onEdit }) => {
  const { value, handleChange, setValue } = useTags();
  const [blogName, setBlogName] = useState('');
  const history = useHistory();
  const [blogText, setBlogText] = useState('');
  const [blogFile, setBlogFile] = useState(null);
  const [suggestedTagIds, setSuggestedTagIds] = useState([]);
  const [suggesting, setSuggesting] = useState(false);
  const debounceRef = useRef(null);
  const safetyTimerRef = useRef(null);
  const autoSelectedTagIdsRef = useRef([]);

  useEffect(() => {
    api.getTags()
      .then(tags => {
        setValue(tags.map(tag => ({ ...tag, value: false })));
      });
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!blogName.trim() && !blogText.trim()) {
      setSuggestedTagIds([]);
      setValue(prev => prev.map(tag => (
        autoSelectedTagIdsRef.current.includes(Number(tag.id))
          ? { ...tag, value: false }
          : tag
      )));
      autoSelectedTagIdsRef.current = [];
      return;
    }
    setSuggesting(true);
    if (safetyTimerRef.current) clearTimeout(safetyTimerRef.current);
    safetyTimerRef.current = setTimeout(() => setSuggesting(false), 20000);
    debounceRef.current = setTimeout(() => {
      api.suggestTags({ name: blogName, text: blogText })
        .then(res => {
          const ids = (res.tags || [])
            .slice(0, 3)
            .map(t => Number(t.id));
          const previousAutoIds = autoSelectedTagIdsRef.current;
          setSuggestedTagIds(ids);
          setValue(prev => prev.map(tag => ({
            ...tag,
            value: (
              (tag.value && !previousAutoIds.includes(Number(tag.id))) ||
              ids.includes(Number(tag.id))
            ),
          })));
          autoSelectedTagIdsRef.current = ids;
        })
        .catch(() => {})
        .finally(() => {
          setSuggesting(false);
          if (safetyTimerRef.current) clearTimeout(safetyTimerRef.current);
        });
    }, 800);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      if (safetyTimerRef.current) clearTimeout(safetyTimerRef.current);
    };
  }, [blogName, blogText]);

  const handleTagChange = id => {
    autoSelectedTagIdsRef.current = autoSelectedTagIdsRef.current.filter(
      tagId => tagId !== Number(id)
    );
    handleChange(id);
  };

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
            handleChange={handleTagChange}
          />
          {suggesting && (
            <p style={{ fontSize: '13px', color: '#999', marginTop: '4px' }}>
              Нейросеть подбирает теги...
            </p>
          )}
          {suggestedTagIds.length > 0 && !suggesting && (
            <p style={{ fontSize: '13px', color: '#2e7d32', marginTop: '4px', marginBottom: '12px' }}>
              Нейросеть рекомендовала теги: выделенные отмечены автоматически
            </p>
          )}
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
