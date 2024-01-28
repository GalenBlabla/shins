'use client'

// pages/landing.js
import Head from 'next/head';
import Image from 'next/image';
import Link from 'next/link';
import Navbar from './components/navbar';
export default function LandingPage() {
  return (
    <div className='' >
      <div className="navbar bg-base-100" >
        <div className="navbar-start">

          <a className="btn btn-ghost text-xl">深斯科技</a>
        </div>

        <div className="navbar-end">
          <Link href="/login" legacyBehavior>
            <a className="inline-block px-7 py-3 bg-blue-600 text-white font-medium text-sm leading-snug uppercase rounded shadow-md hover:bg-blue-700 hover:shadow-lg focus:bg-blue-700 focus:shadow-lg focus:outline-none focus:ring-0 active:bg-blue-800 active:shadow-lg transition duration-150 ease-in-out">
              登录
            </a>
          </Link>
        </div>
      </div>

      <div className="hero min-h-screen" style={{ backgroundImage: 'url(/hero.jpg)' }}>
        <div className="hero-overlay bg-opacity-60"></div>
        <div className="hero-content text-center text-neutral-content">
          <div className="max-w-md">
            <h1 className="mb-5 text-5xl font-bold">欢迎使用深斯AI</h1>
            <p className="mb-5">我们坚信AI即未来</p>
            <Link href="/login" legacyBehavior>
              <a className="inline-block px-7 py-3 bg-blue-600 text-white font-medium text-sm leading-snug uppercase rounded shadow-md hover:bg-blue-700 hover:shadow-lg focus:bg-blue-700 focus:shadow-lg focus:outline-none focus:ring-0 active:bg-blue-800 active:shadow-lg transition duration-150 ease-in-out">
                开始使用
              </a>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
