<template>
  <div class="card">
    <h2>🔐 Nouveau mot de passe</h2>

    <input
      v-model="password"
      type="password"
      placeholder="Nouveau mot de passe"
    />

    <input
      v-model="confirmPassword"
      type="password"
      placeholder="Confirmer mot de passe"
    />

    <button
      class="btn btn-primary"
      @click="changer"
    >
      Changer mot de passe
    </button>

  </div>
</template>

<script setup>

import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const router = useRouter()

const password = ref('')
const confirmPassword = ref('')

async function changer() {

  if (password.value !== confirmPassword.value) {
    alert('Mot de passe tsy mitovy')
    return
  }

  if (!route.query.uid || !route.query.token) {
    alert('Lien invalide')
    return
  }

  try {
    await api.post('/auth/reset-password/', {
      uid: route.query.uid,
      token: route.query.token,
      password: password.value
    })

    alert('Mot de passe changé ✔')
    router.push('/login')

  } catch (e) {
    console.log(e)
    alert('Erreur reset password')
  }
}
</script>