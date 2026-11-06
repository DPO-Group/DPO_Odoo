# Changelog

## [1.2.0](https://github.com/DPO-Group/DPO_Odoo/releases/tag/v1.2.0)

### Added

- Release for Odoo v19.0, delivered as DPO Pay Extras, an extension of the DPO payment provider built into Odoo 19.
- Configurable Pay URL, service description, blocked payment methods (bank transfer and PayPal), and payment time limit.
- Customer street address and phone in the DPO payment request.

### Fixed

- Confirmed DPO payments using the transaction token so returned checkouts complete instead of remaining unconfirmed.
- Handled missing payment amounts so Odoo records an error state instead of failing with a server error.
- Shown a clear error with DPO's explanation when DPO refuses to create a payment token.

## [1.1.1](https://github.com/DPO-Group/DPO_Odoo/releases/tag/v1.1.1)

### Fixed

- Issues with empty address strings.
- Reference to Odoo 17 in the manifest.

## [1.1.0](https://github.com/DPO-Group/DPO_Odoo/releases/tag/v1.1.0)

### Added

- Release for Odoo v18.0.

## [1.0.3](https://github.com/DPO-Group/DPO_Odoo/releases/tag/v1.0.3)

### Added

- Release for Odoo v17.0.

### Fixed

- Bug fixes and improvements.

## [1.0.2](https://github.com/DPO-Group/DPO_Odoo/releases/tag/v1.0.2)

### Fixed

- Fix invalid PnrID reference.

## [1.0.1](https://github.com/DPO-Group/DPO_Odoo/releases/tag/v1.0.1)

### Added

- Release for Odoo v16.0.

## [1.0.0](https://github.com/DPO-Group/DPO_Odoo/releases/tag/v1.0.0)

### Added

- Initial release.
