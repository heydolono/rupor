import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import styles from './styles.module.css';

const Textarea2 = ({ onChange, placeholder, label, disabled, textareaClassName, labelClassName, value }) => {
    const [inputValue, setInputValue] = useState(value);

    const handleValueChange = (e) => {
        const value = e.target.value;
        setInputValue(value);
        onChange(e);
    };

    useEffect(() => {
        if (value !== inputValue) {
            setInputValue(value);
        }
    }, [value]);

    return (
        <div className={styles.textareaContainer}>
            <label className={cn(styles.textareaLabel, labelClassName)}>
                {label && <div className={styles.textareaLabelText}>{label}</div>}
                <textarea
                    rows="8"
                    value={inputValue}
                    className={cn(styles.textareaField, textareaClassName)}
                    onChange={handleValueChange}
                    placeholder={placeholder}
                    disabled={disabled}
                />
            </label>
        </div>
    );
};

export default Textarea2;
