'use client'
import React, { useEffect, useRef, useState, useCallback } from 'react'
import { useChat } from 'ai/react'
import Navbar from '../../components/navbar'
import { useRouter } from 'next/navigation'
import { useCompletion } from 'ai/react'
export default function Chat () {
  const [formData, setFormData] = useState({
    sender: '',
    recipient: '',
    relationship: '',
    festival: '',
  })
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

  const [messages, setMessages] = useState([])
  const router = useRouter()

  // Function to handle completion (AI generation)
  const checkAndPublish = useCallback(async (messageContent) => {
    // Call to your AI service to generate a message
    // Replace with your actual API call
    const stream = await complete(messageContent) // Assuming this returns a stream
    let newContent = ''
    const response = await fetch('/api/completion', {
      method: 'POST',
      body: JSON.stringify({ prompt: messageContent }),
      headers: { 'Content-Type': 'application/json' },
    })
    const data = await response.json()
    return data.text // Assuming the API returns a response with a 'text' field
  }, [complete])

  const handleFormInputChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
  }

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token')
    if (!accessToken) {
      router.push('../login')
    }
  }, [router])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    const messageContent = `生成祝福语: ${formData.sender} 致 ${formData.recipient} 的 ${formData.festival} 祝福`
    const completion = await checkAndPublish(messageContent)
    setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: completion }])
  }

  // Scroll to the bottom of the message list
  const endOfMessagesRef = useRef(null)
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div>
      <Navbar title='Shensi-AI写作-祝福语生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        {/* Rest of the component */}
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">

          <p className="mb-6 text-gray-500">AI节日祝福语生成器，快速生成具有温馨感和独特性的节日祝福语</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">祝福人*</label>
              <input type="text" name="sender" placeholder="您的名字" className="input input-bordered w-full" value={formData.sender} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">被祝福人*</label>
              <input type="text" name="recipient" placeholder="接受祝福的名字" className="input input-bordered w-full" value={formData.recipient} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">关系*</label>
              <select name="relationship" className="select select-bordered w-full" value={formData.relationship} onChange={handleFormInputChange}>
                <option value="">请选择关系</option>
                <option value="父母">父母</option>
                <option value="朋友">朋友</option>
                <option value="子女">子女</option>
                <option value="同事">同事</option>
              </select>
            </div>
            <div>
              <label className="text-gray-700">节日类型*</label>
              <select name="festival" className="select select-bordered w-full" value={formData.festival} onChange={handleFormInputChange}>
                <option value="">请选择节日</option>
                <option value="春节">春节</option>
                <option value="元宵">元宵</option>
                <option value="生日">生日</option>
                <option value="中秋">中秋</option>
              </select>
            </div>
            <button type="submit" className="btn w-full">生成祝福</button>
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
