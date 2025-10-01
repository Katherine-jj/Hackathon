FROM node:18

WORKDIR /app

# Ставим все зависимости, включая devDependencies
COPY package*.json ./
RUN npm install --include=dev

# Копируем код
COPY . .

# Указываем порт Vite
EXPOSE 5173

# Запуск через npx, чтобы точно использовался локальный vite
CMD ["npx", "vite", "dev", "--host", "0.0.0.0"]
