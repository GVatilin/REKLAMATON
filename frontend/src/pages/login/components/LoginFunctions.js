import axios from "axios"

export async function registerUser(email, username, password) {
    if (!username || !email || !password) {
        return "Все поля должны быть заполнены"
    }
    try {
        await axios.post(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/register`, {
            email: email,
            username: username,
            password: password
        }, {
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        })
        return ""
    } catch (error) {
        if (error.response) {          
            if (error.response.status === 400) {
                return "Почта или имя пользователя уже занято"
            } else if (error.response.status === 422 && error.response.data.detail[0].type === "string_too_short") {
                return "Минимальная длина пароля - 8 символов"
            } else if (error.response.status === 422 && error.response.data.detail[0].input === email) {
                return "Введите реальную почту"
            }
        }
        return "Сетевая ошибка или сервер не ответил"
    }
}

export async function loginUser(username, password) {
    if (!username || !password) {
        return "Все поля должны быть заполнены"
    }
    try {
        const res = await axios.post(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/token`, {
            username: username,
            password: password
        }, {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        })
        const token = res.data.access_token
        localStorage.setItem("chronoJWTToken", token)
        return ""
    } catch (error) {
        if (error.response) {          
            if (error.response.status === 401) {
                return "Введен невеный пароль или почта"
            }
        } else {
            return "Сетевая ошибка или сервер не ответил"
        }
    }
}