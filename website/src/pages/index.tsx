import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/chapter-1/intro">
            Start Learning - 5min ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Physical AI & Humanoid Robotics: From Digital Intelligence to Embodied Machines">
      <HomepageHeader />
      <main className={styles.main}>
        <section className={styles.features}>
          <div className="container padding-vert--xl">
            <div className="row">
              <div className="col col--4">
                <div className="text--center padding-horiz--md">
                  <h2>Physical AI</h2>
                  <p>Learn how artificial intelligence becomes embodied in physical machines that interact with the real world.</p>
                </div>
              </div>
              <div className="col col--4">
                <div className="text--center padding-horiz--md">
                  <h2>Humanoid Robotics</h2>
                  <p>Explore the architecture and control systems that enable human-like robots to navigate and interact with their environment.</p>
                </div>
              </div>
              <div className="col col--4">
                <div className="text--center padding-horiz--md">
                  <h2>Simulation → Real World</h2>
                  <p>Master the simulation-first approach that enables safe and efficient development of robotic systems.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.roadmap}>
          <div className="container padding-vert--md text--center">
            <h1>Learning Roadmap</h1>
            <br></br>
            <div className="row">
              <div className="col col--4">
                <h3>Foundation</h3>
                <p>Physical AI concepts, difference from digital AI, embodied intelligence principles</p>
              </div>
              <div className="col col--4">
                <h3>Architecture</h3>
                <p>ROS 2 communication systems, robotic nervous system, node interactions</p>
              </div>
              <div className="col col--4">
                <h3>Simulation</h3>
                <p>Digital twins, physics engines, sensor simulation, safe testing environments</p>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.capstone}>
          <div className="container padding-vert--lg text--center">
            <h2>Capstone Outcome</h2>
            <p>By the end of this course, you'll be able to build and deploy embodied AI systems that bridge the gap between digital intelligence and physical reality.</p>
            <div className="margin-vert--lg">
              <Link
                className="button button--primary button--lg"
                to="/docs/chapter-1/intro">
                Begin Your Journey
              </Link>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
