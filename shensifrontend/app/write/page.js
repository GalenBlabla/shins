'use client'
import React, { useEffect, useState } from "react"
import Link from 'next/link'
import Navbar from "../components/navbar"
import Image from 'next/image'

import { useRouter } from 'next/navigation'
export default function ArticleMenu () {

  const cards = [
    // 社交媒体类
    {
      title: "AI新媒体回答生成器",
      text: "AI新媒体回答生成器，一键生成简明扼要、实用性强的新媒体干货式回答文案",
      imageUrl: "/xiezuo.webp",
      link: './write/huida'
    },
    {
      title: "AI新媒体问题生成器",
      text: "AI新媒体问题生成器，一键生成准确、专业、通俗的新媒体问题",
      imageUrl: "/xiezuo.webp",
      link: './write/wenti'
    },
    {
      title: "AI文章标题生成器",
      text: "AI文章标题生成器，一键生成引人注目的新媒体文章标题",
      imageUrl: "/xiezuo.webp",
      link: './write/biaoti'
    },

    // 写作类
    {
      title: "小学生作文写作",
      text: "您只需要输入作文的标题和需要的字数就可以帮您生成一篇感情丰富，生动真实的作文。",
      imageUrl: "/xiezuo.webp",
      link: './write/article'
    },
    {
      title: "AI诗歌生成器",
      text: "AI诗歌生成器，一键生成优美的诗歌",
      imageUrl: "/xiezuo.webp",
      link: './write/poets'
    },
    {
      title: "AI节日祝福语生成器",
      text: "AI节日祝福语生成器，快速生成具有温馨感和独特性的节日祝福语",
      imageUrl: "/xiezuo.webp",
      link: './write/fortune'
    },
    {
      title: "AI对联生成器",
      text: "AI对联生成器，根据上联内容自动生成内容呼应、对仗工整的下联",
      imageUrl: "/xiezuo.webp",
      link: './write/duilian'
    },
    {
      title: "AI专业论文生成器",
      text: "输入论文标题和关键词，在短时间内生成高质量的专业论文内容",
      imageUrl: "/xiezuo.webp",
      link: './write/lunwen'
    },
    {
      title: "AI文献综述生成器",
      text: "帮助您在短时间内轻松撰写出高质量的论文文献综述",
      imageUrl: "/xiezuo.webp",
      link: './write/wenxian'
    },
    {
      title: "AI文章风格润色工具",
      text: "帮助用户快速改进文章的语言表达风格和整体质量",
      imageUrl: "/xiezuo.webp",
      link: './write/runse'
    },
    {
      title: "AI句子续写工具",
      text: "帮助用户续写句子或扩展句子，适用于写作、小说创作、广告文案等领域",
      imageUrl: "/xiezuo.webp",
      link: './write/jvzi'
    },
    {
      title: "AI种草文案生成器",
      text: "AI种草文案生成器，一键生成文笔优美、内容丰富的种草文案",
      imageUrl: "/xiezuo.webp",
      link: './write/zhongcao'
    },
    {
      title: "AI创意故事生成器",
      text: "AI创意故事生成器，一键生成情节生动、结构完整的创意故事内容",
      imageUrl: "/xiezuo.webp",
      link: './write/chuangyi'
    },
    {
      title: "AI散文生成器",
      text: "AI散文生成器，一键生成平实自然、意境深远的散文作品",
      imageUrl: "/xiezuo.webp",
      link: './write/sanwen'
    },
    {
      title: "AI内容改写工具",
      text: "利用人工智能算法和自然语言处理技术，快速改写原文内容",
      imageUrl: "/xiezuo.webp",
      link: './write/neirong'
    },
    {
      title: "AI藏头诗生成器",
      text: "AI藏头诗生成器，一键生成文笔优美、富有趣味的藏头诗",
      imageUrl: "/xiezuo.webp",
      link: './write/cangtoushi'
    },
    {
      title: "AI对联生成器",
      text: "AI对联生成器，根据上联内容自动生成内容呼应、对仗工整的下联",
      imageUrl: "/xiezuo.webp",
      link: './write/duilian'
    },

    // 教育/文学类
    {
      title: "AI社会实践报告生成器",
      text: "帮助学生更高效、规范地撰写社会实践报告，提高报告的质量和可读性",
      imageUrl: "/xiezuo.webp",
      link: './write/shijian'
    },
    {
      title: "AI教学计划生成器",
      text: "提高教学计划制定效率，减轻教师工作负担",
      imageUrl: "/xiezuo.webp",
      link: './write/jiaoxuejihua'
    },

    // 工作类
    {
      title: "AI日报周报生成器",
      text: "AI日报周报生成器，一键生成内容丰富的工作日报、周报",
      imageUrl: "/xiezuo.webp",
      link: './write/zhoubao'
    },
    {
      title: "AI文章要点生成器",
      text: "AI文章要点生成器，帮助用户快速梳理文章的主旨、要点",
      imageUrl: "/xiezuo.webp",
      link: './write/yaodian'
    },
    {
      title: "AI文章摘要生成器",
      text: "AI文章摘要生成器，自动提取文章的主体内容，生成简洁、准确、通俗易懂的文章摘要",
      imageUrl: "/xiezuo.webp",
      link: './write/zhaiyao'
    },

    // 短视频类
    {
      title: "AI短视频脚本生成器",
      text: "帮助用户快速改进文章的语言表达风格和整体质量",
      imageUrl: "/xiezuo.webp",
      link: './write/jiaoben'
    },
    {
      title: "AI视频标题生成器",
      text: "快速生成符合要求的视频标题，无需花费大量时间和精力去思考",
      imageUrl: "/xiezuo.webp",
      link: './write/biaoti'
    },

    // 电商类
    {
      title: "AI广告语生成器",
      text: "借助AI广告语生成器，一键生成各类创意吸睛广告语",
      imageUrl: "/xiezuo.webp",
      link: './write/guanggao'
    },
    {
      title: "AI产品亮点生成器",
      text: "AI产品亮点生成器，自动提取产品的亮点和优势，帮助用户对产品进行推广和宣传",
      imageUrl: "/xiezuo.webp",
      link: './write/liangdian'
    },
    {
      title: "AI产品核心价值生成器",
      text: "AI产品核心价值生成器，自动识别产品的特点和亮点，确定产品的核心价值和优势",
      imageUrl: "/xiezuo.webp",
      link: './write/hexinjiazhi'
    },
    {
      title: "AI产品特性描述生成器",
      text: "AI产品特性描述生成器，自动识别产品的特性和功能，确定产品的核心要素和特点",
      imageUrl: "/xiezuo.webp",
      link: './write/texing'
    },
    {
      title: "AI产品卖点生成器",
      text: "AI产品卖点生成器，自动生成具有吸引力和卖点的产品描述",
      imageUrl: "/xiezuo.webp",
      link: './write/maidian'
    },
    {
      title: "AI电商产品简介生成器",
      text: "AI电商产品简介生成器，快速生成具有吸引力的电商产品描述和卖点文案",
      imageUrl: "/xiezuo.webp",
      link: './write/jianjie'
    },
    {
      title: "AI商品评价生成器",
      text: "AI商品评价生成器，快速生成具有吸引力的好评内容，提高商品的美誉度和销量",
      imageUrl: "/xiezuo.webp",
      link: './write/pingjia'
    },
    {
      title: "AI达人买家测评生成器",
      text: "帮助您在短时间内轻松撰写出高质量的评测内容",
      imageUrl: "/xiezuo.webp",
      link: './write/pingce'
    },

    // 娱乐类
    {
      title: "AI幽默回复",
      text: "AI幽默回复，根据对方的话语自动生成诙谐幽默的回复话术",
      imageUrl: "/xiezuo.webp",
      link: './write/youmo'
    },
    {
      title: "AI星座占卜师",
      text: "AI星座占卜师，为用户提供星座占卜、运势预测、性格分析等服务",
      imageUrl: "/xiezuo.webp",
      link: './write/zhanbu'
    },
    {
      title: "AI疯狂星期四文案生成器",
      text: "AI疯狂星期四文案生成器，一键生成富有创意和吸引力的肯德基疯狂星期四文案",
      imageUrl: "/xiezuo.webp",
      link: './write/fengkuang'
    },
    {
      title: "AI旅游攻略生成器",
      text: "AI旅游攻略生成器，一键生成高质量的新媒体平台旅游攻略",
      imageUrl: "/xiezuo.webp",
      link: './write/lvyou'
    },
    {
      title: "AI邮件生成器",
      text: "AI邮件生成器，一键生成各种类型的电子邮件内容",
      imageUrl: "/xiezuo.webp",
      link: './write/youjian'
    },
    {
      title: "AI打卡文案生成器",
      text: "AI打卡文案生成器，一键生成内容丰富景点打卡文案内容",
      imageUrl: "/xiezuo.webp",
      link: './write/daka'
    },
    {
      title: "AI干货分享文案生成器",
      text: "AI干货分享文案生成器，一键生成形式多样、内容实用的干货分享类文案",
      imageUrl: "/xiezuo.webp",
      link: './write/ganhuo'
    },
    {
      title: "AI美食探店文案生成器",
      text: "快速生成高质量的美食探店文章，提高店铺曝光率和知名度",
      imageUrl: "/xiezuo.webp",
      link: './write/tandian'
    },
  ]

  const router = useRouter()
  useEffect(() => {
    const accessToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (!accessToken) {
      router.push('../login')
    } else {
      fetchUserData(accessToken) // Call fetchUserData with accessToken
    }
  }, [router])
  function fetchUserData () {
    // 从localStorage获取access_token和token_type
    const accessToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

    const tokenType = typeof window !== 'undefined' ? localStorage.getItem('token_type') : null
    // 检查确保我们有token
    if (accessToken && tokenType) {
      // 设置请求的headers
      const authHeader = `${tokenType} ${accessToken}`
      const backend = process.env.NEXT_PUBLIC_BACK_END
      // 发起请求
      fetch(backend + '/users/me', {
        method: 'GET',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          if (response.ok) {

            return response.json() // 如果响应是JSON，这里将其解析
          }
          throw new Error('Network response was not ok.')
        })
        .then(userData => {

          localStorage.setItem('key', userData.bound_keys)
          console.log(userData.bound_keys)
        })
        .catch(error => {
          console.error('There has been a problem with your fetch operation:', error)
        })
    } else {
      console.error('No access token or token type available in localStorage')
    }
  }




  return (
    <div className=" ">
      <Navbar title='深斯AI写作'></Navbar>
      <h1 className="text-5xl font-bold m-8 text-center mb-6">深斯 AI 写作</h1>
      <div className="flex flex-wrap justify-center gap-4 m-8 p-4">

        {cards.map((card, index) => (
          <div key={index} className="card max-w-xs md:max-w-xs lg:w-1/5 bg-base-100 shadow-xl">
            <figure className="px-10 pt-10">
              <Image src={card.imageUrl} alt="Shoes" className="rounded-xl" width={500} height={500} />
            </figure>
            <div className="card-body items-center text-center">
              <h2 className="card-title">{card.title}</h2>
              <p>{card.text}</p>
              <div className="card-actions">
                <Link href={card.link}>
                  <button className="btn btn-primary">开始使用</button>
                </Link>
              </div>
            </div>
          </div>

        ))}
      </div>
    </div>


  )
}
