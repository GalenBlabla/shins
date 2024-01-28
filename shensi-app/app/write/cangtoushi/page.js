'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function AcrosticPoemGenerator () {
  const [formData, setFormData] = useState({
    inputText: '高考加油', // 示例默认值
    poemLength: '五言', // 示例默认值
  })

  const [poemContent, setPoemContent] = useState('')
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
    const messageContent = `生成藏头诗: 文字 "${formData.inputText}"，诗词字数 "${formData.poemLength}"...`
    setPoemContent('') // 清空现有内容
    const stream = await complete(messageContent) // 假设这返回一个流
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // 将每个块附加到新内容上
      setPoemContent(prevContent => prevContent + chunk) // 逐步更新藏头诗内容
    }
    return newContent // 如果直接更新状态，这可能不是必要的
  }, [complete, formData.inputText, formData.poemLength])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-AI藏头诗生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">AI藏头诗生成器，一键生成文笔优美、富有趣味的藏头诗</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">请输入你想要的文字*</label>
              <input type="text" name="inputText" placeholder="如：高考加油" className="input input-bordered w-full" value={formData.inputText} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">诗词字数*</label>
              <select name="poemLength" className="select select-bordered w-full" value={formData.poemLength} onChange={handleFormInputChange}>
                <option value="五言">五言</option>
                <option value="七言">七言</option>
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
