import React from 'react';
import Head from 'next/head';
import AuthForm from '../../components/auth/AuthForm';

export default function Login() {
  return (
    <>
      <Head>
        <title>Sign In - Creator Community Platform</title>
        <meta name="description" content="Sign in to your Creator Community Platform account" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <AuthForm mode="login" />
    </>
  );
}
