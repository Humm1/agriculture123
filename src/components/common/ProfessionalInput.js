import React from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity } from 'react-native';
import { theme, layout, typography, components } from '../../theme/theme';

/**
 * Professional Input Component for Agricultural Applications
 */
export const ProfessionalInput = ({
  label,
  value,
  onChangeText,
  placeholder,
  error,
  helperText,
  icon,
  rightIcon,
  onRightIconPress,
  variant = 'outlined', // outlined, filled, underlined
  multiline = false,
  numberOfLines = 1,
  keyboardType = 'default',
  secureTextEntry = false,
  disabled = false,
  required = false,
  style,
  inputStyle,
  labelStyle,
  ...props
}) => {
  const containerStyles = [
    styles.container,
    style,
  ];

  const inputContainerStyles = [
    styles.inputContainer,
    styles[`${variant}InputContainer`],
    error && styles.errorInputContainer,
    disabled && styles.disabledInputContainer,
  ];

  const inputStyles = [
    styles.input,
    styles[`${variant}Input`],
    multiline && styles.multilineInput,
    disabled && styles.disabledInput,
    inputStyle,
  ];

  const labelStyles = [
    styles.label,
    error && styles.errorLabel,
    disabled && styles.disabledLabel,
    labelStyle,
  ];

  return (
    <View style={containerStyles}>
      {label && (
        <Text style={labelStyles}>
          {label}
          {required && <Text style={styles.requiredMark}> *</Text>}
        </Text>
      )}
      
      <View style={inputContainerStyles}>
        {icon && <View style={styles.leftIcon}>{icon}</View>}
        
        <TextInput
          style={inputStyles}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={theme.colors.placeholder}
          multiline={multiline}
          numberOfLines={numberOfLines}
          keyboardType={keyboardType}
          secureTextEntry={secureTextEntry}
          editable={!disabled}
          {...props}
        />
        
        {rightIcon && (
          <TouchableOpacity 
            style={styles.rightIcon} 
            onPress={onRightIconPress}
            disabled={!onRightIconPress}
          >
            {rightIcon}
          </TouchableOpacity>
        )}
      </View>
      
      {(error || helperText) && (
        <Text style={[styles.helperText, error && styles.errorText]}>
          {error || helperText}
        </Text>
      )}
    </View>
  );
};

/**
 * Search Input Component for Agricultural Applications
 */
export const SearchInput = ({
  value,
  onChangeText,
  onSubmit,
  placeholder = "Search...",
  showFilter = false,
  onFilterPress,
  style,
  ...props
}) => {
  return (
    <View style={[styles.searchContainer, style]}>
      <View style={styles.searchInputContainer}>
        <View style={styles.searchIcon}>
          <Text style={styles.searchIconText}>🔍</Text>
        </View>
        
        <TextInput
          style={styles.searchInput}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={theme.colors.placeholder}
          returnKeyType="search"
          onSubmitEditing={onSubmit}
          {...props}
        />
        
        {value.length > 0 && (
          <TouchableOpacity 
            style={styles.clearButton}
            onPress={() => onChangeText('')}
          >
            <Text style={styles.clearButtonText}>×</Text>
          </TouchableOpacity>
        )}
      </View>
      
      {showFilter && (
        <TouchableOpacity style={styles.filterButton} onPress={onFilterPress}>
          <Text style={styles.filterButtonText}>⚙</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

/**
 * Form Group Component for organizing related inputs
 */
export const FormGroup = ({
  title,
  children,
  style,
  titleStyle,
  ...props
}) => {
  return (
    <View style={[styles.formGroup, style]} {...props}>
      {title && (
        <Text style={[styles.formGroupTitle, titleStyle]}>
          {title}
        </Text>
      )}
      <View style={styles.formGroupContent}>
        {children}
      </View>
    </View>
  );
};

/**
 * Select Input Component (Dropdown-like)
 */
export const SelectInput = ({
  label,
  value,
  options = [],
  onSelect,
  placeholder = "Select an option",
  error,
  disabled = false,
  required = false,
  style,
  ...props
}) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const selectedOption = options.find(option => option.value === value);

  const handleSelect = (optionValue) => {
    onSelect(optionValue);
    setIsOpen(false);
  };

  return (
    <View style={[styles.container, style]}>
      {label && (
        <Text style={[styles.label, error && styles.errorLabel]}>
          {label}
          {required && <Text style={styles.requiredMark}> *</Text>}
        </Text>
      )}
      
      <TouchableOpacity
        style={[
          styles.selectButton,
          error && styles.errorInputContainer,
          disabled && styles.disabledInputContainer,
        ]}
        onPress={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
      >
        <Text style={[
          styles.selectButtonText,
          !selectedOption && styles.placeholderText,
          disabled && styles.disabledText,
        ]}>
          {selectedOption ? selectedOption.label : placeholder}
        </Text>
        <Text style={styles.selectArrow}>
          {isOpen ? '▲' : '▼'}
        </Text>
      </TouchableOpacity>
      
      {isOpen && (
        <View style={styles.selectOptions}>
          {options.map((option) => (
            <TouchableOpacity
              key={option.value}
              style={[
                styles.selectOption,
                option.value === value && styles.selectedOption,
              ]}
              onPress={() => handleSelect(option.value)}
            >
              <Text style={[
                styles.selectOptionText,
                option.value === value && styles.selectedOptionText,
              ]}>
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
      
      {error && (
        <Text style={styles.errorText}>{error}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  // Base Input Styles
  container: {
    marginBottom: layout.componentSpacing,
  },

  label: {
    ...typography.body2,
    color: theme.colors.text,
    marginBottom: 8,
    fontWeight: '500',
  },

  requiredMark: {
    color: theme.colors.error,
  },

  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: layout.borderRadius.medium,
    backgroundColor: theme.colors.surface,
  },

  input: {
    flex: 1,
    ...typography.body1,
    color: theme.colors.text,
    paddingVertical: 12,
    paddingHorizontal: 16,
  },

  multilineInput: {
    paddingVertical: 16,
    textAlignVertical: 'top',
  },

  leftIcon: {
    paddingLeft: 16,
    paddingRight: 8,
  },

  rightIcon: {
    paddingRight: 16,
    paddingLeft: 8,
  },

  helperText: {
    ...typography.caption,
    color: theme.colors.textSecondary,
    marginTop: 4,
    marginLeft: 4,
  },

  // Input Variants
  outlinedInputContainer: {
    borderWidth: 1,
    borderColor: theme.colors.border,
  },

  filledInputContainer: {
    backgroundColor: theme.colors.surfaceVariant,
  },

  underlinedInputContainer: {
    borderBottomWidth: 2,
    borderBottomColor: theme.colors.border,
    borderRadius: 0,
    backgroundColor: 'transparent',
  },

  outlinedInput: {
    backgroundColor: 'transparent',
  },

  filledInput: {
    backgroundColor: 'transparent',
  },

  underlinedInput: {
    backgroundColor: 'transparent',
    paddingHorizontal: 0,
  },

  // States
  errorInputContainer: {
    borderColor: theme.colors.error,
  },

  disabledInputContainer: {
    backgroundColor: theme.colors.disabled,
    opacity: 0.6,
  },

  disabledInput: {
    color: theme.colors.textSecondary,
  },

  errorLabel: {
    color: theme.colors.error,
  },

  disabledLabel: {
    color: theme.colors.textSecondary,
  },

  errorText: {
    color: theme.colors.error,
  },

  // Search Input Styles
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: layout.componentSpacing,
  },

  searchInputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surfaceVariant,
    borderRadius: layout.borderRadius.large,
    paddingHorizontal: 16,
    height: 48,
  },

  searchIcon: {
    marginRight: 12,
  },

  searchIconText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },

  searchInput: {
    flex: 1,
    ...typography.body1,
    color: theme.colors.text,
    height: '100%',
  },

  clearButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: theme.colors.textSecondary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },

  clearButtonText: {
    color: theme.colors.textOnPrimary,
    fontSize: 16,
    fontWeight: 'bold',
  },

  filterButton: {
    width: 48,
    height: 48,
    borderRadius: layout.borderRadius.large,
    backgroundColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12,
  },

  filterButtonText: {
    color: theme.colors.textOnPrimary,
    fontSize: 18,
  },

  // Form Group Styles
  formGroup: {
    marginBottom: layout.sectionSpacing,
  },

  formGroupTitle: {
    ...typography.h6,
    color: theme.colors.text,
    marginBottom: layout.componentSpacing,
  },

  formGroupContent: {
    // Additional styling for form group content
  },

  // Select Input Styles
  selectButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: layout.borderRadius.medium,
    borderWidth: 1,
    borderColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },

  selectButtonText: {
    ...typography.body1,
    color: theme.colors.text,
    flex: 1,
  },

  selectArrow: {
    ...typography.body2,
    color: theme.colors.textSecondary,
    marginLeft: 8,
  },

  placeholderText: {
    color: theme.colors.placeholder,
  },

  disabledText: {
    color: theme.colors.textSecondary,
  },

  selectOptions: {
    marginTop: 4,
    backgroundColor: theme.colors.surface,
    borderRadius: layout.borderRadius.medium,
    borderWidth: 1,
    borderColor: theme.colors.border,
    ...layout.shadow.medium,
  },

  selectOption: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.borderLight,
  },

  selectedOption: {
    backgroundColor: theme.colors.surfaceVariant,
  },

  selectOptionText: {
    ...typography.body1,
    color: theme.colors.text,
  },

  selectedOptionText: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
});

export default ProfessionalInput;