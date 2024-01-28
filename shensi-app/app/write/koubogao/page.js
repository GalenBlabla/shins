'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function ShortVideoScriptGenerator () {
  const [formData, setFormData] = useState({
    videoTopic: '鼓励对于孩子来说有多重要', // 示例默认值
    keywords: '鼓励可以提高孩子的自信心 更能感受父母的爱 更从容地面对生活', // 示例默认值
  })

  const [scriptContent, setScriptContent] = useState('')

  const [key, setKey] = useState('')
  useEffect(() => {
    // 在组件挂载后从 localStorage 中获取数据
    const storedKey = localStorage.getItem('key')
    if (storedKey) {
      setKey(storedKey)
    }
  }, [])
  const { complete, completion } = useCompletion({
    api: '/api/completion',
    headers: {
      'Authorization': key,
      // 其他头部信息
    },
  })


  const handleFormInputChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
  }

  const router = useRouter()
  useEffect(() => {
    const accessToken = localStorage.getItem('access_token')
    if (!accessToken) {
      router.push('../login')
    }
  }, [router])

  const checkAndPublish = useCallback(async () => {
    const messageContent = `生成短视频口播稿: 视频主题 "${formData.videoTopic}"，关键词 "${formData.keywords}"...`
    setScriptContent('') // 清空现有内容
    const stream = await complete(messageContent) // 假设这返回一个流
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // 将每个块附加到新内容上
      setScriptContent(prevContent => prevContent + chunk) // 逐步更新视频口播稿内容
    }
    return newContent // 如果直接更新状态，这可能不是必要的
  }, [complete, formData.videoTopic, formData.keywords])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-AI短视频口播稿生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">快速生成高质量的口播稿，提高创作效率和质量</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">视频主题*</label>
              <input type="text" name="videoTopic" placeholder="鼓励对于孩子来说有多重要" className="input input-bordered w-full" value={formData.videoTopic} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">关键词*</label>
              <textarea name="keywords" placeholder="鼓励可以提高孩子的自信心 更能感受父母的爱 更从容地面对生活" className="textarea textarea-bordered w-full" value={formData.keywords} onChange={handleFormInputChange} />
            </div>

            <button type="submit" className="btn w-full">生成内容</button>
          </form>
        </div>
        <div className="w-full mt-2 flex justify-center items-center">
          <div className="p-3 mb-2 bg-white rounded-lg shadow w-full max-w-3xl">
            <div className="flex justify-center">
              <textarea className="text-gray-800 w-full h-64" value={completion} readOnly />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
