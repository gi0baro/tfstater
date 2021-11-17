<template>
  <div class="state-list-element">
    <div class="element">
      <span class="name">
        {{ state.name }}
      </span>
      <span v-if="locked" class="lock">
        Locked
      </span>
    </div>
    <div class="ctl">
      <!-- <div class="btn-outer lock"> -->
        <confirm-button class="lock" @tap="actionLock">
          {{ lockText }}
        </confirm-button>
      <!-- </div> -->
      <!-- <div class="btn-outer delete"> -->
        <confirm-button class="delete" @tap="actionDelete">
          Delete
        </confirm-button>
      <!-- </div> -->
    </div>
  </div>
</template>

<script>
import ConfirmButton from './ConfirmButton.vue'

export default {
  name: 'StateListElement',
  components: {
    ConfirmButton
  },
  props: {
    state: {
      type: Object
    }
  },
  computed: {
    locked() {
      return this.state.lock_id !== null
    },
    lockText() {
      return this.locked ? "Unlock" : "Lock"
    }
  },
  methods: {
    actionLock() {
      this.$emit(this.locked ? "unlock" : "lock")
    },
    actionDelete() {
      this.$emit("delete")
    }
  }
}
</script>
