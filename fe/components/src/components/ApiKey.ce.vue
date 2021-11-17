<template>
  <div class="element">
    <div class="date">
      {{ created_at }}
    </div>
    <div class="value">
      {{ value }}
    </div>
    <div class="ctl">
      <confirm-button @tap="deleteAction">
        Delete
      </confirm-button>
    </div>
  </div>
</template>

<script>
import ConfirmButton from './ConfirmButton.vue'

export default {
  name: 'ApiKey',
  components: {
    ConfirmButton
  },
  props: {
    created_at: {
      type: String
    },
    value: {
      type: String
    },
    delete_url: {
      type: String
    }
  },
  methods: {
    deleteAction() {
      window.location.href = this.delete_url
    }
  }
}
</script>

<style scoped>
.element {
  @apply w-full flex border border-solid border-gray-400 rounded px-8 py-4 mb-4;
}
.element .date {
  @apply flex flex-1 items-center;
}
.element .value {
  @apply flex items-center justify-end text-sm text-gray-400;
}
.element .ctl {
  @apply w-32 flex items-center justify-end;
}
.element .ctl:deep() .btn {
  @apply py-1 px-4 flex items-center cursor-pointer border border-solid border-pink-500 text-pink-500 dark:border-pink-400 dark:text-pink-400 rounded focus:outline-none;
}
.element .ctl:deep() .btn.confirm {
  @apply bg-pink-200 dark:bg-pink-600 dark:text-gray-50;
}
</style>
