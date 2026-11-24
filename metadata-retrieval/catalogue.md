# Synthetic asset descriptions

### larch-ticket
Larch Support ticket. SQLite schema: larch_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [larch-account](#larch-account).

### yarrow-line
Yarrow Order line. SQLite schema: yarrow_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [yarrow-orders](#yarrow-orders).

### cedar-orders
Cedar Sales order. SQLite schema: cedar_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok2'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [cedar-bridge](#cedar-bridge), contains items [cedar-line](#cedar-line), settles with [cedar-credit](#cedar-credit).

### fennel-credit
Fennel Refund / credit event. SQLite schema: fennel_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled0'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [fennel-orders](#fennel-orders), policy defined by [fennel-policy](#fennel-policy).

### dahlia-account
Dahlia Account. SQLite schema: dahlia_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [dahlia-bridge](#dahlia-bridge), opens cases [dahlia-ticket](#dahlia-ticket).

### thyme-credit
Thyme Refund / credit event. SQLite schema: thyme_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled4'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [thyme-orders](#thyme-orders), policy defined by [thyme-policy](#thyme-policy).

### hazel-orders
Hazel Sales order. SQLite schema: hazel_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok3'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [hazel-bridge](#hazel-bridge), contains items [hazel-line](#hazel-line), settles with [hazel-credit](#hazel-credit).

### cedar-wide
Cedar Sales analytics dashboard export. SQLite schema: cedar_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [cedar-orders](#cedar-orders), item source [cedar-line](#cedar-line).

### umber-account
Umber Account. SQLite schema: umber_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [umber-bridge](#umber-bridge), opens cases [umber-ticket](#umber-ticket).

### quince-credit
Quince Refund / credit event. SQLite schema: quince_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled1'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [quince-orders](#quince-orders), policy defined by [quince-policy](#quince-policy).

### quince-ticket
Quince Support ticket. SQLite schema: quince_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [quince-account](#quince-account).

### iris-partner
Iris Marketplace partner. SQLite schema: iris_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### aster-account
Aster Account. SQLite schema: aster_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [aster-bridge](#aster-bridge), opens cases [aster-ticket](#aster-ticket).

### pine-policy
Pine Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [pine-credit](#pine-credit), uses orders [pine-orders](#pine-orders).

### larch-partner
Larch Marketplace partner. SQLite schema: larch_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### pine-credit
Pine Refund / credit event. SQLite schema: pine_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled0'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [pine-orders](#pine-orders), policy defined by [pine-policy](#pine-policy).

### fennel-line
Fennel Order line. SQLite schema: fennel_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [fennel-orders](#fennel-orders).

### yarrow-wide
Yarrow Sales analytics dashboard export. SQLite schema: yarrow_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [yarrow-orders](#yarrow-orders), item source [yarrow-line](#yarrow-line).

### willow-line
Willow Order line. SQLite schema: willow_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [willow-orders](#willow-orders).

### pine-line
Pine Order line. SQLite schema: pine_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [pine-orders](#pine-orders).

### iris-policy
Iris Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [iris-credit](#iris-credit), uses orders [iris-orders](#iris-orders).

### pine-bridge
Pine Buyer identity bridge. SQLite schema: pine_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [pine-account](#pine-account), links checkout [pine-orders](#pine-orders).

### nettle-bridge
Nettle Buyer identity bridge. SQLite schema: nettle_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [nettle-account](#nettle-account), links checkout [nettle-orders](#nettle-orders).

### umber-policy
Umber Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [umber-credit](#umber-credit), uses orders [umber-orders](#umber-orders).

### maple-policy
Maple Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [maple-credit](#maple-credit), uses orders [maple-orders](#maple-orders).

### grove-account
Grove Account. SQLite schema: grove_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [grove-bridge](#grove-bridge), opens cases [grove-ticket](#grove-ticket).

### aster-bridge
Aster Buyer identity bridge. SQLite schema: aster_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [aster-account](#aster-account), links checkout [aster-orders](#aster-orders).

### violet-account
Violet Account. SQLite schema: violet_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [violet-bridge](#violet-bridge), opens cases [violet-ticket](#violet-ticket).

### elm-bridge
Elm Buyer identity bridge. SQLite schema: elm_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [elm-account](#elm-account), links checkout [elm-orders](#elm-orders).

### oak-ticket
Oak Support ticket. SQLite schema: oak_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [oak-account](#oak-account).

### iris-wide
Iris Sales analytics dashboard export. SQLite schema: iris_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [iris-orders](#iris-orders), item source [iris-line](#iris-line).

### briar-partner
Briar Marketplace partner. SQLite schema: briar_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### spruce-line
Spruce Order line. SQLite schema: spruce_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [spruce-orders](#spruce-orders).

### cedar-line
Cedar Order line. SQLite schema: cedar_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [cedar-orders](#cedar-orders).

### fennel-wide
Fennel Sales analytics dashboard export. SQLite schema: fennel_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [fennel-orders](#fennel-orders), item source [fennel-line](#fennel-line).

### umber-credit
Umber Refund / credit event. SQLite schema: umber_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled0'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [umber-orders](#umber-orders), policy defined by [umber-policy](#umber-policy).

### violet-wide
Violet Sales analytics dashboard export. SQLite schema: violet_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [violet-orders](#violet-orders), item source [violet-line](#violet-line).

### quince-orders
Quince Sales order. SQLite schema: quince_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok0'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [quince-bridge](#quince-bridge), contains items [quince-line](#quince-line), settles with [quince-credit](#quince-credit).

### larch-policy
Larch Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [larch-credit](#larch-credit), uses orders [larch-orders](#larch-orders).

### iris-orders
Iris Sales order. SQLite schema: iris_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok0'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [iris-bridge](#iris-bridge), contains items [iris-line](#iris-line), settles with [iris-credit](#iris-credit).

### umber-wide
Umber Sales analytics dashboard export. SQLite schema: umber_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [umber-orders](#umber-orders), item source [umber-line](#umber-line).

### spruce-partner
Spruce Marketplace partner. SQLite schema: spruce_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### kite-ticket
Kite Support ticket. SQLite schema: kite_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [kite-account](#kite-account).

### nettle-partner
Nettle Marketplace partner. SQLite schema: nettle_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### spruce-ticket
Spruce Support ticket. SQLite schema: spruce_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [spruce-account](#spruce-account).

### umber-orders
Umber Sales order. SQLite schema: umber_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok0'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [umber-bridge](#umber-bridge), contains items [umber-line](#umber-line), settles with [umber-credit](#umber-credit).

### pine-account
Pine Account. SQLite schema: pine_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [pine-bridge](#pine-bridge), opens cases [pine-ticket](#pine-ticket).

### umber-ticket
Umber Support ticket. SQLite schema: umber_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [umber-account](#umber-account).

### briar-policy
Briar Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [briar-credit](#briar-credit), uses orders [briar-orders](#briar-orders).

### kite-wide
Kite Sales analytics dashboard export. SQLite schema: kite_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [kite-orders](#kite-orders), item source [kite-line](#kite-line).

### hazel-bridge
Hazel Buyer identity bridge. SQLite schema: hazel_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [hazel-account](#hazel-account), links checkout [hazel-orders](#hazel-orders).

### nettle-policy
Nettle Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [nettle-credit](#nettle-credit), uses orders [nettle-orders](#nettle-orders).

### cedar-credit
Cedar Refund / credit event. SQLite schema: cedar_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled2'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [cedar-orders](#cedar-orders), policy defined by [cedar-policy](#cedar-policy).

### rowan-wide
Rowan Sales analytics dashboard export. SQLite schema: rowan_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [rowan-orders](#rowan-orders), item source [rowan-line](#rowan-line).

### thyme-partner
Thyme Marketplace partner. SQLite schema: thyme_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### grove-orders
Grove Sales order. SQLite schema: grove_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok2'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [grove-bridge](#grove-bridge), contains items [grove-line](#grove-line), settles with [grove-credit](#grove-credit).

### violet-policy
Violet Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [violet-credit](#violet-credit), uses orders [violet-orders](#violet-orders).

### kite-line
Kite Order line. SQLite schema: kite_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [kite-orders](#kite-orders).

### umber-line
Umber Order line. SQLite schema: umber_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [umber-orders](#umber-orders).

### larch-line
Larch Order line. SQLite schema: larch_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [larch-orders](#larch-orders).

### hazel-line
Hazel Order line. SQLite schema: hazel_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [hazel-orders](#hazel-orders).

### dahlia-line
Dahlia Order line. SQLite schema: dahlia_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [dahlia-orders](#dahlia-orders).

### nettle-account
Nettle Account. SQLite schema: nettle_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [nettle-bridge](#nettle-bridge), opens cases [nettle-ticket](#nettle-ticket).

### yarrow-policy
Yarrow Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [yarrow-credit](#yarrow-credit), uses orders [yarrow-orders](#yarrow-orders).

### willow-partner
Willow Marketplace partner. SQLite schema: willow_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### fennel-orders
Fennel Sales order. SQLite schema: fennel_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok1'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [fennel-bridge](#fennel-bridge), contains items [fennel-line](#fennel-line), settles with [fennel-credit](#fennel-credit).

### aster-policy
Aster Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [aster-credit](#aster-credit), uses orders [aster-orders](#aster-orders).

### briar-orders
Briar Sales order. SQLite schema: briar_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok1'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [briar-bridge](#briar-bridge), contains items [briar-line](#briar-line), settles with [briar-credit](#briar-credit).

### maple-ticket
Maple Support ticket. SQLite schema: maple_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [maple-account](#maple-account).

### larch-bridge
Larch Buyer identity bridge. SQLite schema: larch_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [larch-account](#larch-account), links checkout [larch-orders](#larch-orders).

### rowan-account
Rowan Account. SQLite schema: rowan_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [rowan-bridge](#rowan-bridge), opens cases [rowan-ticket](#rowan-ticket).

### juniper-account
Juniper Account. SQLite schema: juniper_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [juniper-bridge](#juniper-bridge), opens cases [juniper-ticket](#juniper-ticket).

### nettle-ticket
Nettle Support ticket. SQLite schema: nettle_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [nettle-account](#nettle-account).

### iris-ticket
Iris Support ticket. SQLite schema: iris_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [iris-account](#iris-account).

### quince-line
Quince Order line. SQLite schema: quince_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [quince-orders](#quince-orders).

### quince-partner
Quince Marketplace partner. SQLite schema: quince_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### aster-orders
Aster Sales order. SQLite schema: aster_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok0'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [aster-bridge](#aster-bridge), contains items [aster-line](#aster-line), settles with [aster-credit](#aster-credit).

### quince-policy
Quince Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [quince-credit](#quince-credit), uses orders [quince-orders](#quince-orders).

### rowan-policy
Rowan Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [rowan-credit](#rowan-credit), uses orders [rowan-orders](#rowan-orders).

### oak-line
Oak Order line. SQLite schema: oak_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [oak-orders](#oak-orders).

### briar-ticket
Briar Support ticket. SQLite schema: briar_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [briar-account](#briar-account).

### rowan-orders
Rowan Sales order. SQLite schema: rowan_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok1'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [rowan-bridge](#rowan-bridge), contains items [rowan-line](#rowan-line), settles with [rowan-credit](#rowan-credit).

### rowan-partner
Rowan Marketplace partner. SQLite schema: rowan_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### kite-policy
Kite Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [kite-credit](#kite-credit), uses orders [kite-orders](#kite-orders).

### aster-wide
Aster Sales analytics dashboard export. SQLite schema: aster_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [aster-orders](#aster-orders), item source [aster-line](#aster-line).

### fennel-policy
Fennel Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [fennel-credit](#fennel-credit), uses orders [fennel-orders](#fennel-orders).

### hazel-account
Hazel Account. SQLite schema: hazel_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [hazel-bridge](#hazel-bridge), opens cases [hazel-ticket](#hazel-ticket).

### nettle-wide
Nettle Sales analytics dashboard export. SQLite schema: nettle_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [nettle-orders](#nettle-orders), item source [nettle-line](#nettle-line).

### violet-ticket
Violet Support ticket. SQLite schema: violet_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [violet-account](#violet-account).

### maple-line
Maple Order line. SQLite schema: maple_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [maple-orders](#maple-orders).

### cedar-partner
Cedar Marketplace partner. SQLite schema: cedar_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### violet-partner
Violet Marketplace partner. SQLite schema: violet_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### spruce-policy
Spruce Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [spruce-credit](#spruce-credit), uses orders [spruce-orders](#spruce-orders).

### grove-wide
Grove Sales analytics dashboard export. SQLite schema: grove_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [grove-orders](#grove-orders), item source [grove-line](#grove-line).

### nettle-line
Nettle Order line. SQLite schema: nettle_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [nettle-orders](#nettle-orders).

### oak-credit
Oak Refund / credit event. SQLite schema: oak_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled4'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [oak-orders](#oak-orders), policy defined by [oak-policy](#oak-policy).

### oak-wide
Oak Sales analytics dashboard export. SQLite schema: oak_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [oak-orders](#oak-orders), item source [oak-line](#oak-line).

### dahlia-wide
Dahlia Sales analytics dashboard export. SQLite schema: dahlia_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [dahlia-orders](#dahlia-orders), item source [dahlia-line](#dahlia-line).

### quince-wide
Quince Sales analytics dashboard export. SQLite schema: quince_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [quince-orders](#quince-orders), item source [quince-line](#quince-line).

### briar-line
Briar Order line. SQLite schema: briar_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [briar-orders](#briar-orders).

### maple-credit
Maple Refund / credit event. SQLite schema: maple_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled2'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [maple-orders](#maple-orders), policy defined by [maple-policy](#maple-policy).

### kite-bridge
Kite Buyer identity bridge. SQLite schema: kite_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [kite-account](#kite-account), links checkout [kite-orders](#kite-orders).

### fennel-partner
Fennel Marketplace partner. SQLite schema: fennel_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### cedar-account
Cedar Account. SQLite schema: cedar_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [cedar-bridge](#cedar-bridge), opens cases [cedar-ticket](#cedar-ticket).

### kite-account
Kite Account. SQLite schema: kite_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [kite-bridge](#kite-bridge), opens cases [kite-ticket](#kite-ticket).

### elm-ticket
Elm Support ticket. SQLite schema: elm_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [elm-account](#elm-account).

### elm-credit
Elm Refund / credit event. SQLite schema: elm_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled4'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [elm-orders](#elm-orders), policy defined by [elm-policy](#elm-policy).

### willow-ticket
Willow Support ticket. SQLite schema: willow_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [willow-account](#willow-account).

### cedar-bridge
Cedar Buyer identity bridge. SQLite schema: cedar_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [cedar-account](#cedar-account), links checkout [cedar-orders](#cedar-orders).

### elm-policy
Elm Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [elm-credit](#elm-credit), uses orders [elm-orders](#elm-orders).

### willow-policy
Willow Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [willow-credit](#willow-credit), uses orders [willow-orders](#willow-orders).

### briar-wide
Briar Sales analytics dashboard export. SQLite schema: briar_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [briar-orders](#briar-orders), item source [briar-line](#briar-line).

### juniper-policy
Juniper Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [juniper-credit](#juniper-credit), uses orders [juniper-orders](#juniper-orders).

### juniper-orders
Juniper Sales order. SQLite schema: juniper_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok1'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [juniper-bridge](#juniper-bridge), contains items [juniper-line](#juniper-line), settles with [juniper-credit](#juniper-credit).

### dahlia-policy
Dahlia Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [dahlia-credit](#dahlia-credit), uses orders [dahlia-orders](#dahlia-orders).

### yarrow-ticket
Yarrow Support ticket. SQLite schema: yarrow_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [yarrow-account](#yarrow-account).

### oak-orders
Oak Sales order. SQLite schema: oak_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok2'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [oak-bridge](#oak-bridge), contains items [oak-line](#oak-line), settles with [oak-credit](#oak-credit).

### iris-account
Iris Account. SQLite schema: iris_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [iris-bridge](#iris-bridge), opens cases [iris-ticket](#iris-ticket).

### aster-ticket
Aster Support ticket. SQLite schema: aster_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [aster-account](#aster-account).

### iris-credit
Iris Refund / credit event. SQLite schema: iris_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled3'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [iris-orders](#iris-orders), policy defined by [iris-policy](#iris-policy).

### larch-credit
Larch Refund / credit event. SQLite schema: larch_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled1'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [larch-orders](#larch-orders), policy defined by [larch-policy](#larch-policy).

### elm-line
Elm Order line. SQLite schema: elm_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [elm-orders](#elm-orders).

### violet-bridge
Violet Buyer identity bridge. SQLite schema: violet_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [violet-account](#violet-account), links checkout [violet-orders](#violet-orders).

### grove-credit
Grove Refund / credit event. SQLite schema: grove_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled1'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [grove-orders](#grove-orders), policy defined by [grove-policy](#grove-policy).

### thyme-ticket
Thyme Support ticket. SQLite schema: thyme_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [thyme-account](#thyme-account).

### dahlia-bridge
Dahlia Buyer identity bridge. SQLite schema: dahlia_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [dahlia-account](#dahlia-account), links checkout [dahlia-orders](#dahlia-orders).

### juniper-partner
Juniper Marketplace partner. SQLite schema: juniper_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### iris-line
Iris Order line. SQLite schema: iris_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [iris-orders](#iris-orders).

### grove-partner
Grove Marketplace partner. SQLite schema: grove_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### yarrow-orders
Yarrow Sales order. SQLite schema: yarrow_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok3'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [yarrow-bridge](#yarrow-bridge), contains items [yarrow-line](#yarrow-line), settles with [yarrow-credit](#yarrow-credit).

### juniper-wide
Juniper Sales analytics dashboard export. SQLite schema: juniper_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [juniper-orders](#juniper-orders), item source [juniper-line](#juniper-line).

### fennel-account
Fennel Account. SQLite schema: fennel_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [fennel-bridge](#fennel-bridge), opens cases [fennel-ticket](#fennel-ticket).

### willow-bridge
Willow Buyer identity bridge. SQLite schema: willow_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [willow-account](#willow-account), links checkout [willow-orders](#willow-orders).

### cedar-ticket
Cedar Support ticket. SQLite schema: cedar_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [cedar-account](#cedar-account).

### maple-account
Maple Account. SQLite schema: maple_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [maple-bridge](#maple-bridge), opens cases [maple-ticket](#maple-ticket).

### thyme-bridge
Thyme Buyer identity bridge. SQLite schema: thyme_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [thyme-account](#thyme-account), links checkout [thyme-orders](#thyme-orders).

### spruce-account
Spruce Account. SQLite schema: spruce_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [spruce-bridge](#spruce-bridge), opens cases [spruce-ticket](#spruce-ticket).

### grove-policy
Grove Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [grove-credit](#grove-credit), uses orders [grove-orders](#grove-orders).

### maple-orders
Maple Sales order. SQLite schema: maple_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok0'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [maple-bridge](#maple-bridge), contains items [maple-line](#maple-line), settles with [maple-credit](#maple-credit).

### fennel-bridge
Fennel Buyer identity bridge. SQLite schema: fennel_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [fennel-account](#fennel-account), links checkout [fennel-orders](#fennel-orders).

### pine-partner
Pine Marketplace partner. SQLite schema: pine_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### iris-bridge
Iris Buyer identity bridge. SQLite schema: iris_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [iris-account](#iris-account), links checkout [iris-orders](#iris-orders).

### pine-orders
Pine Sales order. SQLite schema: pine_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok3'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [pine-bridge](#pine-bridge), contains items [pine-line](#pine-line), settles with [pine-credit](#pine-credit).

### cedar-policy
Cedar Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [cedar-credit](#cedar-credit), uses orders [cedar-orders](#cedar-orders).

### larch-wide
Larch Sales analytics dashboard export. SQLite schema: larch_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [larch-orders](#larch-orders), item source [larch-line](#larch-line).

### larch-orders
Larch Sales order. SQLite schema: larch_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok3'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [larch-bridge](#larch-bridge), contains items [larch-line](#larch-line), settles with [larch-credit](#larch-credit).

### briar-bridge
Briar Buyer identity bridge. SQLite schema: briar_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [briar-account](#briar-account), links checkout [briar-orders](#briar-orders).

### hazel-partner
Hazel Marketplace partner. SQLite schema: hazel_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### briar-account
Briar Account. SQLite schema: briar_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [briar-bridge](#briar-bridge), opens cases [briar-ticket](#briar-ticket).

### kite-partner
Kite Marketplace partner. SQLite schema: kite_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### aster-line
Aster Order line. SQLite schema: aster_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [aster-orders](#aster-orders).

### elm-wide
Elm Sales analytics dashboard export. SQLite schema: elm_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [elm-orders](#elm-orders), item source [elm-line](#elm-line).

### thyme-policy
Thyme Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [thyme-credit](#thyme-credit), uses orders [thyme-orders](#thyme-orders).

### kite-orders
Kite Sales order. SQLite schema: kite_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok2'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [kite-bridge](#kite-bridge), contains items [kite-line](#kite-line), settles with [kite-credit](#kite-credit).

### larch-account
Larch Account. SQLite schema: larch_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [larch-bridge](#larch-bridge), opens cases [larch-ticket](#larch-ticket).

### spruce-orders
Spruce Sales order. SQLite schema: spruce_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok2'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [spruce-bridge](#spruce-bridge), contains items [spruce-line](#spruce-line), settles with [spruce-credit](#spruce-credit).

### nettle-credit
Nettle Refund / credit event. SQLite schema: nettle_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled3'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [nettle-orders](#nettle-orders), policy defined by [nettle-policy](#nettle-policy).

### hazel-wide
Hazel Sales analytics dashboard export. SQLite schema: hazel_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [hazel-orders](#hazel-orders), item source [hazel-line](#hazel-line).

### dahlia-ticket
Dahlia Support ticket. SQLite schema: dahlia_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [dahlia-account](#dahlia-account).

### quince-bridge
Quince Buyer identity bridge. SQLite schema: quince_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [quince-account](#quince-account), links checkout [quince-orders](#quince-orders).

### aster-credit
Aster Refund / credit event. SQLite schema: aster_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled0'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [aster-orders](#aster-orders), policy defined by [aster-policy](#aster-policy).

### oak-account
Oak Account. SQLite schema: oak_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [oak-bridge](#oak-bridge), opens cases [oak-ticket](#oak-ticket).

### aster-partner
Aster Marketplace partner. SQLite schema: aster_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### elm-orders
Elm Sales order. SQLite schema: elm_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok0'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [elm-bridge](#elm-bridge), contains items [elm-line](#elm-line), settles with [elm-credit](#elm-credit).

### hazel-policy
Hazel Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [hazel-credit](#hazel-credit), uses orders [hazel-orders](#hazel-orders).

### grove-bridge
Grove Buyer identity bridge. SQLite schema: grove_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [grove-account](#grove-account), links checkout [grove-orders](#grove-orders).

### umber-bridge
Umber Buyer identity bridge. SQLite schema: umber_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [umber-account](#umber-account), links checkout [umber-orders](#umber-orders).

### yarrow-credit
Yarrow Refund / credit event. SQLite schema: yarrow_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled3'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [yarrow-orders](#yarrow-orders), policy defined by [yarrow-policy](#yarrow-policy).

### hazel-ticket
Hazel Support ticket. SQLite schema: hazel_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [hazel-account](#hazel-account).

### rowan-line
Rowan Order line. SQLite schema: rowan_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [rowan-orders](#rowan-orders).

### nettle-orders
Nettle Sales order. SQLite schema: nettle_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok1'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [nettle-bridge](#nettle-bridge), contains items [nettle-line](#nettle-line), settles with [nettle-credit](#nettle-credit).

### yarrow-account
Yarrow Account. SQLite schema: yarrow_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [yarrow-bridge](#yarrow-bridge), opens cases [yarrow-ticket](#yarrow-ticket).

### oak-partner
Oak Marketplace partner. SQLite schema: oak_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### maple-bridge
Maple Buyer identity bridge. SQLite schema: maple_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [maple-account](#maple-account), links checkout [maple-orders](#maple-orders).

### spruce-bridge
Spruce Buyer identity bridge. SQLite schema: spruce_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [spruce-account](#spruce-account), links checkout [spruce-orders](#spruce-orders).

### quince-account
Quince Account. SQLite schema: quince_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [quince-bridge](#quince-bridge), opens cases [quince-ticket](#quince-ticket).

### thyme-wide
Thyme Sales analytics dashboard export. SQLite schema: thyme_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [thyme-orders](#thyme-orders), item source [thyme-line](#thyme-line).

### oak-policy
Oak Finance policy memo. Document from Finance. Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.
Related assets: uses payment [oak-credit](#oak-credit), uses orders [oak-orders](#oak-orders).

### rowan-credit
Rowan Refund / credit event. SQLite schema: rowan_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled2'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [rowan-orders](#rowan-orders), policy defined by [rowan-policy](#rowan-policy).

### grove-line
Grove Order line. SQLite schema: grove_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [grove-orders](#grove-orders).

### violet-orders
Violet Sales order. SQLite schema: violet_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok1'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [violet-bridge](#violet-bridge), contains items [violet-line](#violet-line), settles with [violet-credit](#violet-credit).

### fennel-ticket
Fennel Support ticket. SQLite schema: fennel_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [fennel-account](#fennel-account).

### rowan-bridge
Rowan Buyer identity bridge. SQLite schema: rowan_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [rowan-account](#rowan-account), links checkout [rowan-orders](#rowan-orders).

### willow-orders
Willow Sales order. SQLite schema: willow_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok2'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [willow-bridge](#willow-bridge), contains items [willow-line](#willow-line), settles with [willow-credit](#willow-credit).

### grove-ticket
Grove Support ticket. SQLite schema: grove_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [grove-account](#grove-account).

### willow-account
Willow Account. SQLite schema: willow_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [willow-bridge](#willow-bridge), opens cases [willow-ticket](#willow-ticket).

### violet-credit
Violet Refund / credit event. SQLite schema: violet_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled1'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [violet-orders](#violet-orders), policy defined by [violet-policy](#violet-policy).

### dahlia-partner
Dahlia Marketplace partner. SQLite schema: dahlia_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### hazel-credit
Hazel Refund / credit event. SQLite schema: hazel_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled2'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [hazel-orders](#hazel-orders), policy defined by [hazel-policy](#hazel-policy).

### maple-partner
Maple Marketplace partner. SQLite schema: maple_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### briar-credit
Briar Refund / credit event. SQLite schema: briar_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled1'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [briar-orders](#briar-orders), policy defined by [briar-policy](#briar-policy).

### dahlia-orders
Dahlia Sales order. SQLite schema: dahlia_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok3'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [dahlia-bridge](#dahlia-bridge), contains items [dahlia-line](#dahlia-line), settles with [dahlia-credit](#dahlia-credit).

### thyme-account
Thyme Account. SQLite schema: thyme_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [thyme-bridge](#thyme-bridge), opens cases [thyme-ticket](#thyme-ticket).

### thyme-orders
Thyme Sales order. SQLite schema: thyme_orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER). Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='ok3'. Join lines, credits and the dashboard on oid.
Related assets: resolves buyer [thyme-bridge](#thyme-bridge), contains items [thyme-line](#thyme-line), settles with [thyme-credit](#thyme-credit).

### spruce-credit
Spruce Refund / credit event. SQLite schema: spruce_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled3'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [spruce-orders](#spruce-orders), policy defined by [spruce-policy](#spruce-policy).

### juniper-bridge
Juniper Buyer identity bridge. SQLite schema: juniper_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [juniper-account](#juniper-account), links checkout [juniper-orders](#juniper-orders).

### spruce-wide
Spruce Sales analytics dashboard export. SQLite schema: spruce_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [spruce-orders](#spruce-orders), item source [spruce-line](#spruce-line).

### juniper-ticket
Juniper Support ticket. SQLite schema: juniper_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [juniper-account](#juniper-account).

### elm-account
Elm Account. SQLite schema: elm_account(acct TEXT, tier TEXT, region TEXT). CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.
Related assets: maps buyer [elm-bridge](#elm-bridge), opens cases [elm-ticket](#elm-ticket).

### violet-line
Violet Order line. SQLite schema: violet_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [violet-orders](#violet-orders).

### pine-ticket
Pine Support ticket. SQLite schema: pine_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [pine-account](#pine-account).

### willow-credit
Willow Refund / credit event. SQLite schema: willow_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled2'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [willow-orders](#willow-orders), policy defined by [willow-policy](#willow-policy).

### dahlia-credit
Dahlia Refund / credit event. SQLite schema: dahlia_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled3'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [dahlia-orders](#dahlia-orders), policy defined by [dahlia-policy](#dahlia-policy).

### yarrow-partner
Yarrow Marketplace partner. SQLite schema: yarrow_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### yarrow-bridge
Yarrow Buyer identity bridge. SQLite schema: yarrow_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [yarrow-account](#yarrow-account), links checkout [yarrow-orders](#yarrow-orders).

### juniper-line
Juniper Order line. SQLite schema: juniper_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [juniper-orders](#juniper-orders).

### juniper-credit
Juniper Refund / credit event. SQLite schema: juniper_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled4'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [juniper-orders](#juniper-orders), policy defined by [juniper-policy](#juniper-policy).

### willow-wide
Willow Sales analytics dashboard export. SQLite schema: willow_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [willow-orders](#willow-orders), item source [willow-line](#willow-line).

### umber-partner
Umber Marketplace partner. SQLite schema: umber_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### elm-partner
Elm Marketplace partner. SQLite schema: elm_partner(partner_id TEXT, segment TEXT). Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.

### rowan-ticket
Rowan Support ticket. SQLite schema: rowan_ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER). Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.
Related assets: filed by [rowan-account](#rowan-account).

### pine-wide
Pine Sales analytics dashboard export. SQLite schema: pine_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [pine-orders](#pine-orders), item source [pine-line](#pine-line).

### thyme-line
Thyme Order line. SQLite schema: thyme_line(oid INTEGER, sku TEXT, units INTEGER). Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.
Related assets: belongs to order [thyme-orders](#thyme-orders).

### kite-credit
Kite Refund / credit event. SQLite schema: kite_credit(oid INTEGER, cents INTEGER, state TEXT). Payment connector. Several credits may exist for an order. Settled fund movements use state='settled0'. Aggregate matching credits per order before joining to line or dashboard data.
Related assets: credits order [kite-orders](#kite-orders), policy defined by [kite-policy](#kite-policy).

### oak-bridge
Oak Buyer identity bridge. SQLite schema: oak_bridge(buyer TEXT, acct TEXT). Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.
Related assets: resolves account [oak-account](#oak-account), links checkout [oak-orders](#oak-orders).

### maple-wide
Maple Sales analytics dashboard export. SQLite schema: maple_wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER). One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.
Related assets: sourced from [maple-orders](#maple-orders), item source [maple-line](#maple-line).
