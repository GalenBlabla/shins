'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function LiteratureReviewGenerator () {
  const [formData, setFormData] = useState({
    title: '',
    keywords: '',
  })

  const [reviewContent, setReviewContent] = useState('')

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
    const messageContent = `生成文献综述: 题目 "${formData.title}"，关键词 "${formData.keywords}"...`
    setReviewContent('') // Clear existing content
    const stream = await complete(messageContent) // Assuming this returns a stream
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // Append each chunk to the newContent
      setReviewContent(prevContent => prevContent + chunk) // Update the reviewContent state progressively
    }
    return newContent // This may not be necessary if you're updating the state directly
  }, [complete, formData.title, formData.keywords])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-文献综述生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">帮助您在短时间内轻松撰写出高质量的论文文献综述</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">论文题目*</label>
              <input type="text" name="title" placeholder="如：跨栏跑运动的历史沿革与发展趋势" className="input input-bordered w-full" value={formData.title} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">论文关键词*</label>
              <input type="text" name="keywords" placeholder="如：跨栏跑；体育运动；运动史。" className="input input-bordered w-full" value={formData.keywords} onChange={handleFormInputChange} />
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
