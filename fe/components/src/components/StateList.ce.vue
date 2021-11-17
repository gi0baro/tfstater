<template>
  <div class="state-list">
    <div v-if="error" class="error">
      {{ error }}
    </div>
    <div v-if="!error && !loading && !states.length" class="message">
      No states available
    </div>
    <div v-if="!error && states.length" class="wrapper">
      <state-list-element
        v-for="state in states"
        :key="state.id"
        :state="state"
        @lock="lockItem(state)"
        @unlock="unlockItem(state)"
        @delete="deleteItem(state)"
      ></state-list-element>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import StateListElement from './StateListElement.vue'

export default {
  name: 'StateList',
  components: {
    StateListElement
  },
  props: {
    api_endpoint: {
      type: String,
    },
    privileges: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      states: [],
      loading: false,
      page: 1,
      has_more: false,
      error: null
    }
  },
  created() {
    this.http = axios.create({
      validateStatus(status) {
        return (status >= 200 && status < 300) || (status >= 400 && status < 500)
      }
    })
  },
  async mounted() {
    await this.refreshData()
    window.addEventListener('scroll', () => this.handleScroll())
  },
  methods: {
    async getData() {
      try {
        let {status, data} = await this.http.get(
          this.api_endpoint, {params: {page: this.page}}
        )
        if (status == 200) {
          this.states = [ ...this.states, ...data.data ]
          this.has_more = data.meta.has_more
        } else {
          this.error = "an error happened :("
          this.has_more = false
        }
        this.loading = false
      } catch (err) {
        this.error = "something bad happened :("
        this.has_more = false
      }
    },
    async refreshData() {
      this.loading = true
      this.page = 1
      this.has_more = false
      this.states = []
      await this.getData()
    },
    async appendData() {
      this.loading = true
      this.page++
      await this.getData()
    },
    async lockItem(item) {
      try {
        let {status, data} = await this.http.post(
          `${this.api_endpoint}/${item.id}/lock`, {}
        )
        if (status == 201) {
          Object.keys(data).forEach((key) => {
            item[key] = data[key]
          })
        }
      } catch (_) {
        console.log("error locking item")
      }
    },
    async unlockItem(item) {
      try {
        let {status} = await this.http.delete(
          `${this.api_endpoint}/${item.id}/lock`
        )
        if (status == 200) {
          item.lock_id = null
          item.lock_owner = null
          item.locked_at = null
        }
      } catch (_) {
        console.log("error unlock item")
      }
    },
    async deleteItem(item) {
      try {
        let {status} = await this.http.delete(
          `${this.api_endpoint}/${item.id}`
        )
        if (status == 200) {
          await this.refreshData()
        }
      } catch (_) {
        console.log("error deleting item")
      }
    },
    async handleScroll() {
      if (!this.has_more || this.loading) {
        return
      }
      if (document.documentElement.scrollTop >= (document.documentElement.offsetHeight - window.innerHeight) * 0.8) {
        await this.appendData()
      }
    }
  }
}
</script>

<style scoped>
.error {
  @apply text-pink-700 dark:text-pink-400 text-xl text-center mt-16;
}
.message {
  @apply text-gray-400 text-xl text-center mt-16;
}
.state-list {
  @apply w-full container mx-auto py-8;
}
.state-list .wrapper {
  @apply flex flex-col mx-6;
}
.state-list-element {
  @apply flex border border-solid border-gray-400 rounded px-8 py-4 mb-4;
}
.state-list-element:deep() .element {
  @apply flex flex-1 items-center text-xl;
}
.state-list-element:deep() .element .lock {
  @apply ml-4 bg-indigo-200 text-indigo-500 font-semibold text-xs uppercase rounded-full py-1.5 px-3;
}
.state-list-element:deep() .ctl {
  @apply w-32 flex items-center justify-end;
}
/* .state-list-element:deep() .btn-outer {
  @apply flex-none ml-2;
} */
.state-list-element:deep() .ctl .btn {
  @apply px-4 py-1 flex items-center border border-solid rounded border-gray-400 text-gray-200 cursor-pointer ml-4;
}
.state-list-element:deep() .ctl .lock .btn {
  @apply text-indigo-500 border-indigo-500 dark:border-indigo-300 dark:text-indigo-300;
}
.state-list-element:deep() .ctl .delete .btn {
  @apply text-pink-600 border-pink-600 dark:border-pink-400 dark:text-pink-400;
}
.state-list-element:deep() .ctl .btn.confirm {
  @apply bg-pink-200 dark:bg-pink-600 dark:text-gray-50;
}
</style>
