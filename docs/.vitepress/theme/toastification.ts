import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

export default {
    install: (app) => {
        app.use(Toast, {
            toastClassName: "global-message",
            position: 'top-right',
            timeout: 5000,
            closeOnClick: false,
            pauseOnFocusLoss: true,
            pauseOnHover: true,
            draggable: true,
            draggablePercent: 0.6,
            showCloseButtonOnHover: true,
            hideProgressBar: true,
            closeButton: 'button',
            icon: true,
            rtl: false
        })
    }
}