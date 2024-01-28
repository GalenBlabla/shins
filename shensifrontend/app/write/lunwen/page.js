'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function AcademicPaperGenerator () {
  const [formData, setFormData] = useState({
    title: '',
    keywords: '',
  })

  const [paperContent, setPaperContent] = useState('')

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
    const messageContent = `
生成长论文:
标题: "${formData.title}"
关键词: ${formData.keywords.split(',').map(keyword => `"${keyword.trim()}"`).join(', ')}
摘要: [在此处提供简短的论文摘要或概述]
引言: [简要介绍研究的背景和重要性]
主体:
  - 第一部分: [对第一个主题或论点的详细讨论]
  - 第二部分: [对第二个主题或论点的详细讨论]
  - 更多部分: [根据需要添加其他部分]
结论: [总结研究发现和论文的主要观点]
参考文献: [列出参考文献]
`

    setPaperContent('') // Clear existing content
    const stream = await complete(messageContent) // Assuming this returns a stream
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // Append each chunk to the newContent
      setPaperContent(prevContent => prevContent + chunk) // Update the paperContent state progressively
    }
    return newContent // This may not be necessary if you're updating the state directly
  }, [complete, formData.title, formData.keywords])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-专业论文生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">输入论文标题和关键词，快速生成专业论文内容</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">论文标题*</label>
              <input type="text" name="title" placeholder="请输入论文标题" className="input input-bordered w-full" value={formData.title} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">关键词*</label>
              <input type="text" name="keywords" placeholder="请输入关键词" className="input input-bordered w-full" value={formData.keywords} onChange={handleFormInputChange} />
            </div>

            <button type="submit" className="btn w-full">生成论文</button>
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
