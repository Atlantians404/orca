import { motion } from 'framer-motion';

/**
 * A single, restrained reveal-on-scroll wrapper used once per section
 * (not per card) so the page has one quiet rhythm rather than motion
 * scattered across every element.
 */
export default function Reveal({ children, delay = 0, y = 24, className = '' }) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}
