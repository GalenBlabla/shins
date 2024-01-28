# 阶段 1: 构建
# 使用 Node.js 官方镜像作为构建环境
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 yarn.lock 文件
COPY package.json yarn.lock ./

# 安装项目依赖
RUN yarn install --frozen-lockfile

# 复制应用程序代码
COPY . .

# 构建应用程序
RUN yarn build

# 阶段 2: 运行
# 使用更小的 Node.js 镜像来减小最终镜像的体积
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 仅复制构建阶段的产物和必要的文件
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.mjs ./next.config.mjs

# 设置环境变量
ENV NODE_ENV production
ENV PORT 3000

# 暴露容器端口
EXPOSE 3000

# 定义运行应用程序的命令
CMD ["yarn", "start"]
