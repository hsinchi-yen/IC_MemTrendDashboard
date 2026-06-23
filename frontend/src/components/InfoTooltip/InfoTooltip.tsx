export function InfoTooltip({ text }: { text: string }) {
  return (
    <abbr
      title={text}
      style={{
        marginLeft: 6,
        cursor: 'help',
        textDecoration: 'none',
        color: 'var(--color-accent-light)',
        fontWeight: 600,
      }}
    >
      ⓘ
    </abbr>
  )
}