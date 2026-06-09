<template>
  <div class="custom-select-wrapper" ref="selectRef">
    <div class="custom-select-trigger" @click="toggleDropdown">
      <span>{{ selectedLabel }}</span>
      <span class="arrow" :class="{ open: isOpen }">▼</span>
    </div>

    <div v-if="isOpen" class="custom-options-list">
      <div 
        v-for="option in options" 
        :key="option.value"
        :class="['custom-option', { selected: modelValue === option.value }]"
        @click="selectOption(option.value)"
      >
        {{ option.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Пропси: приймаємо масив об'єктів [{ value: '...', label: '...' }] та плейсхолдер
const props = defineProps({
  options: {
    type: Array,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Виберіть значення'
  }
})

// Зв'язуємо v-model батьківського компонента з внутрішнім станом
const modelValue = defineModel()

const isOpen = ref(false)
const selectRef = ref(null)

// Знаходимо текст для поточного вибраного значення
const selectedLabel = computed(() => {
  const found = props.options.find(opt => opt.value === modelValue.value)
  return found ? found.label : props.placeholder
})

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectOption = (value) => {
  modelValue.value = value
  isOpen.value = false
}

// Логіка закриття селекту при кліку в будь-яке інше місце екрана
const handleClickOutside = (event) => {
  if (selectRef.value && !selectRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.custom-select-wrapper {
  position: relative;
  width: 140px; /* Можна регулювати ширину */
  user-select: none;
  font-size: 0.85rem;
}

.custom-select-trigger {
  background-color: #f4f4f5;
  border: 1px solid #dfe1e5;
  border-radius: 6px;
  padding: 6px 10px;
  color: #1a1a1a;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: border-color 0.15s, background-color 0.15s;
}

.custom-select-trigger:hover {
  border-color: #3390ec;
}

.arrow {
  font-size: 0.65rem;
  color: #707579;
  transition: transform 0.2s;
  margin-left: 6px;
}

.arrow.open {
  transform: rotate(180deg);
}

.custom-options-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  background-color: white;
  border: 1px solid #dfe1e5;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 200px;
  overflow-y: auto;
  padding: 4px 0;
}

.custom-option {
  padding: 8px 12px;
  cursor: pointer;
  color: #1a1a1a;
  transition: background-color 0.1s;
}

.custom-option:hover {
  background-color: #f4f4f5;
}

.custom-option.selected {
  background-color: #f4f9fe;
  color: #3390ec;
  font-weight: 600;
}
</style>