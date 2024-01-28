'use client'
import React, { useState, useCallback, useEffect } from 'react'
import Navbar from '../../components/navbar'
import { useCompletion } from 'ai/react'
import { useRouter } from 'next/navigation'

export default function ProductRecommendationCopyGenerator () {
  const [formData, setFormData] = useState({
    category: '通用', // 示例默认值
    productName: 'iPhone 13', // 示例默认值
    productDescription: '灵动岛功能，全天候显示，A16仿生芯片。', // 示例默认值
    contentLength: '中', // 示例默认值
  })

  const [recommendationCopy, setRecommendationCopy] = useState('')
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
    const messageContent = `生成种草文案: 品类 "${formData.category}"，产品名称 "${formData.productName}"，产品描述 "${formData.productDescription}"，文章长度 "${formData.contentLength}"...`
    setRecommendationCopy('') // 清空现有内容
    const stream = await complete(messageContent) // 假设这返回一个流
    let newContent = ''
    for await (const chunk of stream) {
      newContent += chunk // 将每个块附加到新内容上
      setRecommendationCopy(prevContent => prevContent + chunk) // 逐步更新种草文案
    }
    return newContent // 如果直接更新状态，这可能不是必要的
  }, [complete, formData.category, formData.productName, formData.productDescription, formData.contentLength])

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    await checkAndPublish()
  }

  return (
    <div>
      <Navbar title='Shensi-AI写作-AI种草文案生成器'></Navbar>
      <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-xl p-6">
          <p className="mb-6 text-gray-500">AI种草文案生成器，一键生成文笔优美、内容丰富的种草文案</p>
          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="text-gray-700">品类</label>
              <select name="category" className="select select-bordered w-full" value={formData.category} onChange={handleFormInputChange}>
                <option value="通用">通用</option>
                <option value="鞋服包饰">鞋服包饰</option>
                <option value="护肤个护">护肤个护</option>
                <option value="美妆彩妆">美妆彩妆</option>
                <option value="宠物用品">宠物用品</option>
                <option value="家居家装">家居家装</option>
                <option value="母婴育儿">母婴育儿</option>
                <option value="数码产品">数码产品</option>
              </select>
            </div>
            <div>
              <label className="text-gray-700">产品名称*</label>
              <input type="text" name="productName" placeholder="如：iPhone 13" className="input input-bordered w-full" value={formData.productName} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">产品描述</label>
              <textarea name="productDescription" placeholder="如：灵动岛功能，全天候显示，A16仿生芯片。" className="textarea textarea-bordered w-full" value={formData.productDescription} onChange={handleFormInputChange} />
            </div>
            <div>
              <label className="text-gray-700">文章长度</label>
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
