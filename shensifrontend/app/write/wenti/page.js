'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function NewMediaQuestionGenerator () {
  const [formData, setFormData] = useState({
    topic: '',
    audience: '',
  })

  const [generatedQuestion, setGeneratedQuestion] = useState('')

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
    const messageContent = `生成新媒体问题: 话题 "${formData.topic}"，受众 "${formData.audience}"...`
    setGeneratedQuestion('') // 清空现有内容
    const stream = await complete(messageContent) // 假设这返回一个流
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // 将每个块附加到新内容上
      setGeneratedQuestion(prevContent => prevContent + chunk) // 逐步更新生成的问题状态
    }
    return newContent // 如果直接更新状态，这可能不是必要的
  }, [complete, formData.topic, formData.audience])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-AI新媒体问题生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">AI新媒体问题生成器，一键生成准确、专业、通俗的新媒体问题</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">话题*</label>
              <input type="text" name="topic" placeholder="如：比特币价格上涨" className="input input-bordered w-full" value={formData.topic} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">受众*</label>
              <input type="text" name="audience" placeholder="如：黄金投资者" className="input input-bordered w-full" value={formData.audience} onChange={handleFormInputChange} />
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
