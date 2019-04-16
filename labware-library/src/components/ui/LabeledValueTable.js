// @flow
import * as React from 'react'

import { Table, TableEntry, TABLE_COLUMN } from './Table'
import { LabelText, LABEL_TOP, LABEL_LEFT } from './LabelText'
import { Value } from './Value'

import type { TableDirection } from './Table'

export type ValueEntry = {
  label: React.Node,
  value: React.Node,
}

export type LabledValueTableProps = {
  label: React.Node,
  values: Array<ValueEntry>,
  direction?: TableDirection,
  className?: string,
  children?: React.Node,
}

export function LabeledValueTable(props: LabledValueTableProps) {
  const { label, values, direction, className, children } = props

  return (
    <div className={className}>
      <LabelText position={LABEL_TOP}>{label}</LabelText>
      <Table direction={direction || TABLE_COLUMN}>
        {values.map((v, i) => (
          <TableEntry key={i}>
            <LabelText position={LABEL_LEFT}>{v.label}</LabelText>
            <Value>{v.value}</Value>
          </TableEntry>
        ))}
      </Table>
      {children}
    </div>
  )
}
