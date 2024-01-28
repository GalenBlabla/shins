'use client'
import React, { useEffect, useRef } from 'react'
import { useState, useCallback } from 'react'
import Navbar from '../../components/navbar'
import { useChat } from 'ai/react'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'
export default function PoetryGenerator () {
  const [formData, setFormData] = useState({
    theme: '',
    style: '',
  })
  const [content, setContent] = useState('')
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

  const checkAndPublish = useCallback(async (c) => {
    const stream = await complete(c) // Assuming this returns a stream
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // Append each chunk to the newContent
      setContent(prevContent => prevContent + chunk) // Update the content state progressively
    }
    return newContent // This may not be necessary if you're updating the state directly
  }, [complete])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    const messageContent = `以主题“${formData.theme}”和风格“${formData.style}”写一篇“${formData.length}”的小学生作文...`
    setContent('') // Clear existing content
    await checkAndPublish(messageContent)
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-小学生作文生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">AI作文生成器，根据主题和体裁快速写出作文</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">作文主题*</label>
              <input type="text" name="theme" placeholder="请输入作文主题" className="input input-bordered w-full" value={formData.theme} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">作文字数*</label>
              <input type="text" name="length" placeholder="请输入作文字数" className="input input-bordered w-full" value={formData.length} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">作文体裁*</label>
              <select name="style" className="select select-bordered w-full" value={formData.style} onChange={handleFormInputChange}>
                <option value="">请选择体裁</option>
                <option value="记叙文">记叙文</option>
                <option value="说明文">说明文</option>
                <option value="议论文">议论文</option>
                <option value="小说">小说</option>
                <option value="散文">散文</option>
              </select>
            </div>

            <button type="submit" className="btn w-full">生成作文</button>
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
