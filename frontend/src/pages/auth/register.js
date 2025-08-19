import React from 'react';
import Head from 'next/head';
import AuthForm from '../../components/auth/AuthForm';

export default function Register() {
  return (
    <>
      <Head>
        <title>Sign Up - Creator Community Platform</title>
        <meta name="description" content="Join the Creator Community Platform and connect with fellow creators" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <AuthForm mode="register" />
    </>
  );
}
