<template>
  <div class="btn-wrapper">
    <transition name="fade" mode="out-in">
      <div v-if="!confirmable" class="btn" @click="tap">
        <slot></slot>
      </div>
      <div v-else class="btn confirm" @click="tapConfirm">
        Confirm
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'ConfirmButton',
  data() {
    return {
      confirmable: false,
      timeout: null
    }
  },
  methods: {
    tap() {
      this.confirmable = true
      this.timeout = setTimeout(() => this.timeoutExpired(), 5000)
    },
    timeoutExpired() {
      this.confirmable = false
    },
    tapConfirm() {
      clearTimeout(this.timeout)
      this.$emit('tap')
      this.confirmable = false
    }
  }
}
</script>
