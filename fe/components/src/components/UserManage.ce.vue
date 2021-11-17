<template>
  <div class="element">
    <div class="identifier">
      {{ email }}
    </div>
    <div class="role">
      <div v-if="editable" class="edit">
        <select v-model="selectedRole" @change="editAction">
          <option
            v-for="roleDef in roles"
            :key="roleDef.role"
            :value="roleDef.role"
          >{{ roleDef.label }}</option>
        </select>
        <div class="svg-ico">
          <svg class="ico" viewBox="0 0 20 20">
            <path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
          </svg>
        </div>
      </div>
      <div v-else class="label">
        {{ roleLabel }}
      </div>
    </div>
    <div class="ctl">
      <confirm-button v-if="editable" @tap="deleteAction">
        Delete
      </confirm-button>
      <div v-else class="label">
        It's you
      </div>
    </div>
  </div>
</template>

<script>
import ConfirmButton from './ConfirmButton.vue'

export default {
  name: 'UserManage',
  components: {
    ConfirmButton
  },
  props: {
    email: {
      type: String
    },
    role: {
      type: String
    },
    delete_url: {
      type: String
    },
    edit_url: {
      type: String
    },
    editable: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      roleLabels: {
        0: "Member",
        10: "Maintainer"
      },
      selectedRole: this.role
    }
  },
  computed: {
    roleLabel() {
      return this.roleLabels[this.role]
    },
    roles() {
      let rv = []
      Object.keys(this.roleLabels).forEach((key) => {
        rv.push({role: key, label: this.roleLabels[key]})
      })
      return rv
    }
  },
  methods: {
    editAction() {
      window.location.href = `${this.edit_url}?role=${this.selectedRole}`
    },
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
.element .identifier {
  @apply flex flex-1 items-center;
}
.element .role {
  @apply flex items-center justify-end text-sm text-gray-400;
}
.element .role .edit {
  @apply relative;
}
.element .role .edit select {
  @apply appearance-none block pl-2 pr-8 py-1 border-gray-400 bg-gray-100 dark:bg-gray-700 dark:text-gray-100 rounded focus:outline-none;
}
.element .role .edit .svg-ico {
  @apply pointer-events-none absolute inset-y-0 right-0 flex items-center px-2;
}
.element .role .edit .svg-ico .ico {
  @apply h-4 w-4 fill-current;
}
.element .ctl {
  @apply w-32 flex items-center justify-end;
}
.element .ctl .label {
  @apply py-1 text-gray-400;
}
.element .ctl:deep() .btn {
  @apply py-1 px-4 flex items-center cursor-pointer border border-solid border-pink-500 text-pink-500 dark:border-pink-400 dark:text-pink-400 rounded focus:outline-none;
}
.element .ctl:deep() .btn.confirm {
  @apply bg-pink-200 dark:bg-pink-600 dark:text-gray-50;
}
</style>
