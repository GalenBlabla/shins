'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function TravelGuideGenerator () {
  const [formData, setFormData] = useState({
    destination: '',
    days: '',
    contentLength: '中', // 默认选项
  })

  const [generatedGuide, setGeneratedGuide] = useState('')

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
    const messageContent = `生成旅游攻略: 城市/景点 "${formData.destination}"，天数 "${formData.days}"，文案长度 "${formData.contentLength}"...`
    setGeneratedGuide('') // 清空现有内容
    const stream = await complete(messageContent) // 假设这返回一个流
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // 将每个块附加到新内容上
      setGeneratedGuide(prevContent => prevContent + chunk) // 逐步更新生成的旅游攻略状态
    }
    return newContent // 如果直接更新状态，这可能不是必要的
  }, [complete, formData.destination, formData.days, formData.contentLength])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-AI旅游攻略生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">AI旅游攻略生成器，一键生成高质量的新媒体平台旅游攻略</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">城市/景点*</label>
              <input type="text" name="destination" placeholder="如：杭州" className="input input-bordered w-full" value={formData.destination} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">天数*</label>
              <input type="text" name="days" placeholder="如：3" className="input input-bordered w-full" value={formData.days} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">文案长度*</label>
              <select name="contentLength" className="select select-bordered w-full" value={formData.contentLength} onChange={handleFormInputChange}>
                <option value="短">短</option>
                <option value="中">中</option>
                <option value="长">长</option>
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
