import { reactive } from 'vue'

const toast = reactive({
  visible: false,
  message: '',
  type: 'success', // success | error | info | warning
})

let timer = null

export function useToast() {
  function showToast(message, type = 'success', duration = 3500) {
    if (timer) clearTimeout(timer)
    toast.message = message
    toast.type    = type
    toast.visible = true
    timer = setTimeout(() => {
      toast.visible = false
    }, duration)
  }

  return { toast, showToast }
}
