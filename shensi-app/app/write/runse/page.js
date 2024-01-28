'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function StyleEnhancementTool () {
  const [formData, setFormData] = useState({
    keywordsOrSentence: '',
    style: '',
  })

  const [enhancedContent, setEnhancedContent] = useState('')

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
    const messageContent = `改进文章风格: 关键词或中心句 "${formData.keywordsOrSentence}"，应用风格 "${formData.style}"...`
    setEnhancedContent('') // Clear existing content
    const stream = await complete(messageContent) // Assuming this returns a stream
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // Append each chunk to the newContent
      setEnhancedContent(prevContent => prevContent + chunk) // Update the enhancedContent state progressively
    }
    return newContent // This may not be necessary if you're updating the state directly
  }, [complete, formData.keywordsOrSentence, formData.style])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-文章风格润色工具'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">帮助用户快速改进文章的语言表达风格和整体质量</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">关键词或中心句*</label>
              <textarea name="keywordsOrSentence" placeholder="请填写段落相关的关键词或关键句" className="textarea textarea-bordered w-full" value={formData.keywordsOrSentence} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">选择风格*</label>
              <select name="style" className="select select-bordered w-full" value={formData.style} onChange={handleFormInputChange}>
                <option value="">请选择风格</option>
                <option value="专业的">专业的</option>
                <option value="友好的">友好的</option>
                <option value="正式的">正式的</option>
                <option value="非正式的">非正式的</option>
              </select>
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
