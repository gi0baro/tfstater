import { defineCustomElement } from 'vue'
import './index.css'

import StateList from './components/StateList.ce.vue'
import ApiKey from './components/ApiKey.ce.vue'
import UserManage from './components/UserManage.ce.vue'

const ElementStateList = defineCustomElement(StateList)
const ElementApiKey = defineCustomElement(ApiKey)
const ElementUserManage = defineCustomElement(UserManage)


const elements = {
  'state-list': ElementStateList,
  'api-key': ElementApiKey,
  'user-manage': ElementUserManage
}

function register_elements(prefix) {
  Object.keys(elements).forEach((key) => {
    customElements.define(`${prefix}-${key}`, elements[key])
  })
}

register_elements("tfstater")
